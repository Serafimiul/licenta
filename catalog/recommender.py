"""
Content-based + behavior-based product recommender.

Algorithm
---------
For a target product T, every candidate product C is scored by:

    score(C) = w_content * cosine(vec(T), vec(C)) + w_popularity * pop(C)

where vec(P) is a fixed-length numeric feature vector built from:
  - category membership (one-hot over all categories)
  - platform compatibility (multi-hot over all platforms)
  - numeric attributes (int / float / range — range uses midpoint),
    min-max normalized across the catalog so each axis lies in [0, 1]

`pop(C)` is the log-scaled count of OrderItems referencing C, normalized
to [0, 1] across the candidate pool. This is the lightweight
"behavior-based" signal: products other users actually bought rank higher.

The whole computation is in pure Python (no numpy dependency) and runs
in O(N * F) per request where N is the candidate pool size (~200 in
this project) and F is the feature dimension (~50). This is fast
enough to run live without caching.
"""

from __future__ import annotations

import math
from collections import defaultdict

from .models import AttributeDefinition, Category, Platform, Product, ProductAttribute


# Weights for the final score. Sum to 1.0 by convention; tune as needed.
W_CONTENT = 0.75
W_POPULARITY = 0.25


# ──────────────────────────────────────────────────────────────────────
# Feature space construction
# ──────────────────────────────────────────────────────────────────────

def _build_feature_space():
    """
    Returns axis layouts shared by every vector:
      - category_ids: ordered list of category PKs
      - platform_ids: ordered list of platform PKs
      - numeric_attrs: ordered list of (attribute_id, data_type)
      - attr_bounds: {attribute_id: (min_value, max_value)} across catalog
    """
    category_ids = list(Category.objects.values_list('id', flat=True).order_by('id'))
    platform_ids = list(Platform.objects.values_list('id', flat=True).order_by('id'))

    numeric_attrs = list(
        AttributeDefinition.objects
        .filter(data_type__in=('int', 'float', 'range'))
        .values_list('id', 'data_type')
        .order_by('id')
    )

    # Compute min/max per attribute so we can min-max normalize.
    attr_bounds = {}
    for attr_id, dtype in numeric_attrs:
        values = []
        for pa in ProductAttribute.objects.filter(attribute_id=attr_id):
            v = _attribute_value(pa, dtype)
            if v is not None:
                values.append(v)
        if values:
            lo, hi = min(values), max(values)
            attr_bounds[attr_id] = (lo, hi if hi != lo else lo + 1.0)
        else:
            attr_bounds[attr_id] = (0.0, 1.0)

    return category_ids, platform_ids, numeric_attrs, attr_bounds


def _attribute_value(pa: ProductAttribute, dtype: str):
    """Extracts a single float from a ProductAttribute based on its data type."""
    if dtype == 'range':
        if pa.value_min is None or pa.value_max is None:
            return None
        return (pa.value_min + pa.value_max) / 2.0
    if dtype in ('int', 'float'):
        return pa.value_number
    return None


def _vector_for(product: Product, space) -> list:
    """Builds the feature vector for one product against the shared axis layout."""
    category_ids, platform_ids, numeric_attrs, attr_bounds = space

    vec = []

    # 1. category one-hot
    for cid in category_ids:
        vec.append(1.0 if cid == product.category_id else 0.0)

    # 2. platform multi-hot
    product_plat_ids = set(product.compatible_platforms.values_list('id', flat=True))
    for pid in platform_ids:
        vec.append(1.0 if pid in product_plat_ids else 0.0)

    # 3. numeric attributes (normalized)
    attr_values = {
        pa.attribute_id: pa for pa in product.attributes.all()
    }
    for attr_id, dtype in numeric_attrs:
        pa = attr_values.get(attr_id)
        if pa is None:
            vec.append(0.0)
            continue
        raw = _attribute_value(pa, dtype)
        if raw is None:
            vec.append(0.0)
            continue
        lo, hi = attr_bounds[attr_id]
        normalized = (raw - lo) / (hi - lo)
        vec.append(max(0.0, min(1.0, normalized)))

    return vec


# ──────────────────────────────────────────────────────────────────────
# Math helpers
# ──────────────────────────────────────────────────────────────────────

def _cosine(a: list, b: list) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _popularity_scores(candidate_ids: list) -> dict:
    """
    Returns {product_id: pop_score in [0, 1]} based on log(1 + order_item_count).
    Imported lazily to avoid a circular dependency.
    """
    from orders.models import OrderItem

    counts = defaultdict(int)
    rows = (
        OrderItem.objects
        .filter(product_id__in=candidate_ids)
        .values_list('product_id')
    )
    for (pid,) in rows:
        counts[pid] += 1

    if not counts:
        return {pid: 0.0 for pid in candidate_ids}

    logs = {pid: math.log1p(c) for pid, c in counts.items()}
    max_log = max(logs.values()) or 1.0
    return {pid: logs.get(pid, 0.0) / max_log for pid in candidate_ids}


# ──────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────

def recommend_for(product: Product, limit: int = 4) -> list:
    """
    Returns up to `limit` Product objects most similar to `product`,
    using content-based vector similarity blended with behavior-based
    popularity.

    The candidate pool is: every active product in the same parent
    category (or same category if no parent), excluding the target itself.
    This keeps results topically relevant while still allowing cross-
    subcategory suggestions (e.g., from a temperature sensor to a
    humidity sensor — both children of "Senzori").
    """
    # Candidate pool: siblings under the same parent.
    parent = product.category.parent or product.category
    candidates_qs = (
        Product.objects
        .filter(is_active=True)
        .filter(category__in=[parent, *parent.children.all()])
        .exclude(id=product.id)
        .select_related('category')
        .prefetch_related('compatible_platforms', 'attributes__attribute')
    )
    candidates = list(candidates_qs)
    if not candidates:
        return []

    space = _build_feature_space()
    target_vec = _vector_for(product, space)
    pop_scores = _popularity_scores([c.id for c in candidates])

    scored = []
    for cand in candidates:
        sim = _cosine(target_vec, _vector_for(cand, space))
        pop = pop_scores.get(cand.id, 0.0)
        score = W_CONTENT * sim + W_POPULARITY * pop
        scored.append((score, cand))

    # Higher score first; stable on ties.
    scored.sort(key=lambda t: t[0], reverse=True)
    return [c for _, c in scored[:limit]]
