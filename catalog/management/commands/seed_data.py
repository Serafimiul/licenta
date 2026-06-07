from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from decimal import Decimal
import random

from catalog.models import Category, AttributeDefinition, Product, ProductAttribute, Platform
from orders.models import Order, OrderItem

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with realistic automation products data (Romanian)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...\n')
        self.counts = {'categories': 0, 'attributes': 0, 'products': 0, 'users': 0, 'orders': 0}

        with transaction.atomic():
            platforms = self._create_platforms()
            self._create_categories()
            self._create_attributes()
            self._create_products(platforms)
            self._create_users()
            self._create_orders()

        c = self.counts
        self.stdout.write(self.style.SUCCESS(
            f"\nSeed complete: {c['categories']} categories, "
            f"{c['attributes']} attribute definitions, "
            f"{c['products']} products, "
            f"{c['users']} users, "
            f"{c['orders']} orders"
        ))

    # ──────────────────────────────────────────────
    # PLATFORMS
    # ──────────────────────────────────────────────
    def _create_platforms(self):
        data = [
            ('Arduino Uno', 'arduino-uno'),
            ('Arduino Mega', 'arduino-mega'),
            ('ESP8266', 'esp8266'),
            ('ESP32', 'esp32'),
            ('Raspberry Pi', 'raspberry-pi'),
            ('STM32', 'stm32'),
            ('Micro:bit', 'microbit'),
            ('PLC Siemens S7', 'plc-siemens-s7'),
            ('PLC Allen-Bradley', 'plc-allen-bradley'),
        ]
        platforms = {}
        for name, slug in data:
            obj, _ = Platform.objects.get_or_create(name=name, slug=slug)
            platforms[slug] = obj
        self.stdout.write(f'  [OK] Created {len(data)} platforms')
        return platforms

    # ──────────────────────────────────────────────
    # CATEGORIES
    # ──────────────────────────────────────────────
    def _create_categories(self):
        tree = {
            ('Senzori', 'sensors', 'Senzori industriali și hobby pentru măsurare și detecție'): [
                ('Senzori de Temperatură', 'temperature-sensors', 'Senzori digitali și analogici pentru măsurarea temperaturii'),
                ('Senzori de Presiune', 'pressure-sensors', 'Senzori pentru presiune barometrică, relativă și diferențială'),
                ('Senzori de Proximitate', 'proximity-sensors', 'Senzori inductivi, capacitivi, optici și magnetici'),
                ('Senzori de Mișcare', 'motion-sensors', 'Senzori PIR, microunde și accelerometre'),
                ('Senzori de Gaz', 'gas-sensors', 'Senzori pentru detectarea gazelor și calitatea aerului'),
                ('Senzori de Umiditate', 'humidity-sensors', 'Senzori capacitivi și rezistivi pentru umiditate'),
                ('Senzori de Distanță', 'distance-sensors', 'Senzori ultrasonici, IR, laser ToF și LIDAR'),
                ('Senzori de Lumină', 'light-sensors', 'Fotosenzori, senzori UV și IR pentru măsurarea luminii'),
            ],
            ('Actuatoare', 'actuators', 'Motoare, servo-uri, relee și alte dispozitive de acționare'): [
                ('Motoare DC', 'dc-motors', 'Motoare de curent continuu cu și fără encoder'),
                ('Servo Motoare', 'servo-motors', 'Servo-uri micro, standard și digitale'),
                ('Motoare Pas cu Pas', 'stepper-motors', 'Motoare stepper cu control precis al poziției'),
                ('Relee', 'relays', 'Relee electromagnetice și solid-state'),
                ('Solenoizi', 'solenoids', 'Valve și mecanisme cu solenoid'),
            ],
            ('Controllere', 'controllers', 'Microcontrollere, PLC-uri și plăci de dezvoltare'): [
                ('Plăci Arduino', 'arduino-boards', 'Plăci de dezvoltare Arduino oficiale și compatibile'),
                ('Plăci ESP', 'esp-boards', 'Module WiFi/BT bazate pe ESP8266 și ESP32'),
                ('Raspberry Pi', 'raspberry-pi-boards', 'Single board computers Raspberry Pi'),
                ('Module PLC', 'plc-modules', 'Controllere logice programabile industriale'),
            ],
            ('Module de Comunicație', 'communication-modules', 'Module wireless și cu fir pentru comunicație'): [
                ('Module WiFi', 'wifi-modules', 'Module WiFi standalone și shield-uri'),
                ('Module Bluetooth', 'bluetooth-modules', 'Module Bluetooth Classic și BLE'),
                ('Module LoRa', 'lora-modules', 'Module LoRa pentru comunicații pe distanțe lungi'),
                ('Module RS485/Modbus', 'rs485-modules', 'Convertoare și module pentru comunicație industrială'),
            ],
            ('Surse de Alimentare', 'power-supplies', 'Surse de alimentare și convertoare de tensiune'): [
                ('Surse DIN Rail', 'din-rail-psu', 'Surse de alimentare montaj pe șină DIN'),
                ('Convertoare DC-DC', 'dc-dc-converters', 'Convertoare step-up și step-down'),
            ],
        }

        for (pname, pslug, pdesc), children in tree.items():
            parent, created = Category.objects.get_or_create(
                slug=pslug,
                defaults={'name': pname, 'description': pdesc}
            )
            if created:
                self.counts['categories'] += 1
                self.stdout.write(f'  [OK] Created category: {pname}')
            for cname, cslug, cdesc in children:
                child, created = Category.objects.get_or_create(
                    slug=cslug,
                    defaults={'name': cname, 'description': cdesc, 'parent': parent}
                )
                if created:
                    self.counts['categories'] += 1
                    self.stdout.write(f'    [OK] Created subcategory: {cname}')

    # ──────────────────────────────────────────────
    # ATTRIBUTE DEFINITIONS
    # ──────────────────────────────────────────────
    def _create_attributes(self):
        # (name, slug, data_type, unit, is_filterable)
        defs = {
            'temperature-sensors': [
                ('Interval măsurare', 'measure_range', 'range', '°C', True),
                ('Precizie', 'accuracy', 'float', '°C', True),
                ('Interfață comunicație', 'interface', 'string', '', True),
                ('Tensiune alimentare', 'supply_voltage', 'float', 'V', True),
                ('Grad protecție', 'ip_rating', 'string', '', True),
                ('Timp răspuns', 'response_time', 'float', 'ms', False),
                ('Tip senzor', 'sensor_type', 'string', '', True),
            ],
            'pressure-sensors': [
                ('Interval presiune', 'pressure_range', 'range', 'bar', True),
                ('Precizie', 'accuracy', 'float', '%FS', True),
                ('Tip presiune', 'pressure_type', 'string', '', True),
                ('Semnal ieșire', 'output_signal', 'string', '', True),
                ('Tensiune alimentare', 'supply_voltage', 'float', 'V', True),
                ('Mediu compatibil', 'media_compatible', 'string', '', True),
            ],
            'proximity-sensors': [
                ('Distanță detecție', 'detect_distance', 'float', 'mm', True),
                ('Tip senzor', 'sensor_type', 'string', '', True),
                ('Tip ieșire', 'output_type', 'string', '', True),
                ('Tensiune alimentare', 'supply_voltage', 'range', 'V', True),
                ('Frecvență comutare', 'switch_freq', 'float', 'Hz', False),
                ('Grad protecție', 'ip_rating', 'string', '', True),
            ],
            'motion-sensors': [
                ('Unghi detecție', 'detection_angle', 'float', '°', True),
                ('Distanță detecție', 'detect_distance', 'float', 'm', True),
                ('Tip senzor', 'sensor_type', 'string', '', True),
                ('Tensiune alimentare', 'supply_voltage', 'range', 'V', True),
                ('Timp întârziere', 'delay_time', 'range', 's', False),
            ],
            'gas-sensors': [
                ('Gaz detectat', 'gas_type', 'string', '', True),
                ('Interval concentrație', 'ppm_range', 'range', 'ppm', True),
                ('Timp încălzire', 'warmup_time', 'float', 's', False),
                ('Tensiune alimentare', 'supply_voltage', 'float', 'V', True),
                ('Tip ieșire', 'output_type', 'string', '', True),
            ],
            'humidity-sensors': [
                ('Interval umiditate', 'humidity_range', 'range', '%RH', True),
                ('Precizie umiditate', 'humidity_acc', 'float', '%RH', True),
                ('Interval temperatură', 'temp_range', 'range', '°C', True),
                ('Interfață', 'interface', 'string', '', True),
                ('Tip senzor', 'sensor_type', 'string', '', True),
            ],
            'distance-sensors': [
                ('Interval măsurare', 'measure_range', 'range', 'cm', True),
                ('Precizie', 'accuracy', 'float', 'mm', True),
                ('Tehnologie', 'technology', 'string', '', True),
                ('Unghi fascicul', 'beam_angle', 'float', '°', False),
                ('Tensiune alimentare', 'supply_voltage', 'float', 'V', True),
                ('Interfață', 'interface', 'string', '', True),
            ],
            'light-sensors': [
                ('Interval măsurare', 'lux_range', 'range', 'lux', True),
                ('Spectru detectat', 'spectrum', 'string', '', True),
                ('Interfață', 'interface', 'string', '', True),
                ('Tensiune alimentare', 'supply_voltage', 'float', 'V', True),
            ],
            'dc-motors': [
                ('Tensiune nominală', 'voltage', 'float', 'V', True),
                ('Curent nominal', 'current', 'float', 'A', True),
                ('Turație', 'rpm', 'float', 'RPM', True),
                ('Putere', 'power', 'float', 'W', True),
                ('Tip motor', 'motor_type', 'string', '', True),
            ],
            'servo-motors': [
                ('Tensiune alimentare', 'supply_voltage', 'range', 'V', True),
                ('Cuplu', 'torque', 'float', 'kg·cm', True),
                ('Unghi rotație', 'rotation_angle', 'float', '°', True),
                ('Tip servo', 'servo_type', 'string', '', True),
            ],
            'stepper-motors': [
                ('Unghi pas', 'step_angle', 'float', '°', True),
                ('Curent per fază', 'current_phase', 'float', 'A', True),
                ('Cuplu retenție', 'holding_torque', 'float', 'N·m', True),
                ('Număr fire', 'wire_count', 'int', '', True),
            ],
            'relays': [
                ('Tensiune bobină', 'coil_voltage', 'float', 'V', True),
                ('Curent maxim comutat', 'max_current', 'float', 'A', True),
                ('Tensiune max AC', 'max_voltage_ac', 'float', 'V', True),
                ('Tip releu', 'relay_type', 'string', '', True),
            ],
            'arduino-boards': [
                ('Microcontroler', 'mcu', 'string', '', True),
                ('Tensiune operare', 'operating_voltage', 'float', 'V', True),
                ('Pini digitali', 'digital_pins', 'int', '', True),
                ('Pini analogici', 'analog_pins', 'int', '', True),
                ('Memorie Flash', 'flash_memory', 'int', 'KB', True),
                ('Frecvență ceas', 'clock_freq', 'float', 'MHz', True),
                ('Conectivitate', 'connectivity', 'string', '', True),
            ],
            'esp-boards': [
                ('Chip principal', 'main_chip', 'string', '', True),
                ('Memorie Flash', 'flash_memory', 'int', 'MB', True),
                ('RAM', 'ram', 'int', 'KB', True),
                ('Conectivitate', 'connectivity', 'string', '', True),
                ('Pini GPIO', 'gpio_pins', 'int', '', True),
                ('Tensiune alimentare', 'supply_voltage', 'float', 'V', True),
            ],
        }

        for cat_slug, attrs in defs.items():
            try:
                category = Category.objects.get(slug=cat_slug)
            except Category.DoesNotExist:
                continue
            for name, slug, dtype, unit, filterable in attrs:
                _, created = AttributeDefinition.objects.get_or_create(
                    slug=slug, category=category,
                    defaults={
                        'name': name, 'unit': unit,
                        'data_type': dtype, 'is_filterable': filterable,
                    }
                )
                if created:
                    self.counts['attributes'] += 1

        self.stdout.write(f'  [OK] Created {self.counts["attributes"]} attribute definitions')

    # ──────────────────────────────────────────────
    # PRODUCTS
    # ──────────────────────────────────────────────
    def _create_products(self, plat):
        self._seed_temperature_sensors(plat)
        self._seed_pressure_sensors(plat)
        self._seed_proximity_sensors(plat)
        self._seed_motion_sensors(plat)
        self._seed_gas_sensors(plat)
        self._seed_humidity_sensors(plat)
        self._seed_distance_sensors(plat)
        self._seed_light_sensors(plat)
        self._seed_dc_motors(plat)
        self._seed_servo_motors(plat)
        self._seed_stepper_motors(plat)
        self._seed_relays(plat)
        self._seed_arduino_boards(plat)
        self._seed_esp_boards(plat)
        self.stdout.write(f'  [OK] Created {self.counts["products"]} products')

    def _make_product(self, cat_slug, data, plat_map):
        """Helper: creates a product with attributes and platforms."""
        category = Category.objects.get(slug=cat_slug)
        platforms_list = data.pop('platforms', [])
        attrs = data.pop('attrs', {})

        product, created = Product.objects.get_or_create(
            sku=data['sku'],
            defaults={
                'name': data['name'],
                'slug': data['slug'],
                'description': data['description'],
                'price': Decimal(str(data['price'])),
                'stock': data.get('stock', random.randint(10, 80)),
                'manufacturer': data['manufacturer'],
                'category': category,
                'is_active': True,
            }
        )
        if not created:
            return

        self.counts['products'] += 1

        # Set platforms
        platform_objs = [plat_map[s] for s in platforms_list if s in plat_map]
        product.compatible_platforms.set(platform_objs)

        # Set attributes
        for attr_slug, value in attrs.items():
            try:
                attr_def = AttributeDefinition.objects.get(slug=attr_slug, category=category)
            except AttributeDefinition.DoesNotExist:
                continue

            pa_kwargs = {'product': product, 'attribute': attr_def}
            if attr_def.data_type == 'range' and isinstance(value, (list, tuple)):
                pa_kwargs['value_min'] = float(value[0])
                pa_kwargs['value_max'] = float(value[1])
            elif attr_def.data_type in ('int', 'float'):
                pa_kwargs['value_number'] = float(value)
            else:
                pa_kwargs['value_string'] = str(value)

            ProductAttribute.objects.get_or_create(
                product=product, attribute=attr_def,
                defaults=pa_kwargs
            )

    # ---------- Temperature Sensors ----------
    def _seed_temperature_sensors(self, p):
        cat = 'temperature-sensors'
        products = [
            {
                'name': 'DS18B20 Senzor temperatură digital waterproof',
                'slug': 'ds18b20-waterproof',
                'sku': 'TMP-00001',
                'manufacturer': 'Maxim Integrated',
                'price': 12.50,
                'stock': 85,
                'description': 'Senzor digital de temperatură cu interfață 1-Wire într-o capsulă waterproof din oțel inoxidabil. Oferă o precizie de ±0.5°C într-un interval de -55 la +125°C. Ideal pentru măsurarea temperaturii lichidelor, solurilor și mediilor umede. Se poate conecta mai mulți senzori pe un singur pin de date.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp8266', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'measure_range': (-55, 125),
                    'accuracy': 0.5,
                    'interface': 'Digital 1-Wire',
                    'supply_voltage': 3.3,
                    'ip_rating': 'IP67',
                    'response_time': 750.0,
                    'sensor_type': 'Digital IC',
                }
            },
            {
                'name': 'DHT22 Senzor temperatură și umiditate',
                'slug': 'dht22-temperature-humidity',
                'sku': 'TMP-00002',
                'manufacturer': 'Aosong',
                'price': 18.90,
                'stock': 120,
                'description': 'Senzor combinat de temperatură și umiditate cu ieșire digitală calibrată. Oferă măsurări precise în gama -40°C la +80°C cu o precizie de ±0.5°C. Foarte popular în proiectele de monitorizare a mediului ambient. Comunicare simplă pe un singur fir digital.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp8266', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'measure_range': (-40, 80),
                    'accuracy': 0.5,
                    'interface': 'Digital 1-Wire',
                    'supply_voltage': 3.3,
                    'ip_rating': 'IP20',
                    'response_time': 2000.0,
                    'sensor_type': 'Digital IC',
                }
            },
            {
                'name': 'PT100 Senzor temperatură rezistiv industrial',
                'slug': 'pt100-industrial-rtd',
                'sku': 'TMP-00003',
                'manufacturer': 'Jumo',
                'price': 85.00,
                'stock': 30,
                'description': 'Senzor de temperatură rezistiv din platină de clasă industrială pentru aplicații de precizie ridicată. Intervalul extins de -200°C la +600°C îl face potrivit pentru procese industriale, cuptoare și tratament termic. Ieșire 4-20mA compatibilă cu orice PLC industrial.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'measure_range': (-200, 600),
                    'accuracy': 0.3,
                    'interface': '4-20mA',
                    'supply_voltage': 24.0,
                    'ip_rating': 'IP65',
                    'response_time': 150.0,
                    'sensor_type': 'PT100',
                }
            },
            {
                'name': 'BME280 Senzor temperatură/presiune/umiditate I2C',
                'slug': 'bme280-environment-sensor',
                'sku': 'TMP-00004',
                'manufacturer': 'Bosch',
                'price': 22.00,
                'stock': 95,
                'description': 'Senzor combinat pentru temperatură, presiune barometrică și umiditate cu interfață I2C. Consumul ultra-redus de energie îl face ideal pentru stații meteo portabile și dispozitive IoT alimentate pe baterii. Precizia ridicată și dimensiunea mică permit integrarea ușoară în orice proiect.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'measure_range': (-40, 85),
                    'accuracy': 1.0,
                    'interface': 'I2C',
                    'supply_voltage': 3.3,
                    'ip_rating': 'IP20',
                    'response_time': 1000.0,
                    'sensor_type': 'Digital IC',
                }
            },
            {
                'name': 'LM35 Senzor temperatură analog liniar',
                'slug': 'lm35-analog-temperature',
                'sku': 'TMP-00005',
                'manufacturer': 'Texas Instruments',
                'price': 8.50,
                'stock': 150,
                'description': 'Senzor analog de temperatură cu ieșire liniară de 10mV/°C, calibrat direct în grade Celsius. Nu necesită calibrare externă și oferă o precizie tipică de ±0.5°C. Foarte ușor de integrat cu orice microcontroler cu intrare analogică. Soluție economică pentru proiecte simple.',
                'platforms': ['arduino-uno', 'arduino-mega', 'stm32'],
                'attrs': {
                    'measure_range': (-55, 150),
                    'accuracy': 0.5,
                    'interface': 'Analog',
                    'supply_voltage': 5.0,
                    'ip_rating': 'IP20',
                    'response_time': 60.0,
                    'sensor_type': 'Digital IC',
                }
            },
            {
                'name': 'MAX6675 Modul citire termocuplu tip K',
                'slug': 'max6675-thermocouple-k',
                'sku': 'TMP-00006',
                'manufacturer': 'Maxim Integrated',
                'price': 35.00,
                'stock': 45,
                'description': 'Modul de citire pentru termocupluri tip K cu convertor digital MAX6675 integrat. Măsoară temperaturi de la 0°C la 1024°C, ideal pentru monitorizarea cuptoarelor, proceselor de sudare și aplicații de temperatură înaltă. Comunicare prin interfață SPI la viteze mari.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32', 'stm32'],
                'attrs': {
                    'measure_range': (0, 1024),
                    'accuracy': 3.0,
                    'interface': 'SPI',
                    'supply_voltage': 5.0,
                    'ip_rating': 'IP20',
                    'response_time': 220.0,
                    'sensor_type': 'Termocuplu K',
                }
            },
            {
                'name': 'SHT31 Senzor temperatură și umiditate de precizie',
                'slug': 'sht31-precision-temp-humidity',
                'sku': 'TMP-00007',
                'manufacturer': 'Sensirion',
                'price': 45.00,
                'stock': 55,
                'description': 'Senzor digital de precizie ridicată pentru temperatură și umiditate de la Sensirion. Precizia de ±0.3°C și interfața I2C fac din acest senzor alegerea optimă pentru aplicații medicale, HVAC și camere curate. Include un element de încălzire intern pentru regenerare.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'measure_range': (-40, 125),
                    'accuracy': 0.3,
                    'interface': 'I2C',
                    'supply_voltage': 3.3,
                    'ip_rating': 'IP20',
                    'response_time': 500.0,
                    'sensor_type': 'Digital IC',
                }
            },
            {
                'name': 'PT1000 Senzor temperatură RTD industrial IP68',
                'slug': 'pt1000-rtd-industrial-ip68',
                'sku': 'TMP-00008',
                'manufacturer': 'Heraeus',
                'price': 120.00,
                'stock': 20,
                'description': 'Senzor RTD industrial din platină PT1000 cu protecție IP68 pentru medii extreme. Intervalul de -200°C la +850°C și precizia de ±0.1°C îl califică pentru cele mai exigente aplicații industriale. Corp din oțel inoxidabil 316L, rezistent la chimicale și presiune.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'measure_range': (-200, 850),
                    'accuracy': 0.1,
                    'interface': '4-20mA',
                    'supply_voltage': 24.0,
                    'ip_rating': 'IP68',
                    'response_time': 100.0,
                    'sensor_type': 'PT1000',
                }
            },
        ]
        for prod in products:
            self._make_product(cat, prod, p)

    # ---------- Pressure Sensors ----------
    def _seed_pressure_sensors(self, p):
        cat = 'pressure-sensors'
        products = [
            {
                'name': 'MPX5700AP Senzor presiune absolută 700kPa',
                'slug': 'mpx5700ap-absolute-pressure',
                'sku': 'PRS-00001',
                'manufacturer': 'NXP',
                'price': 55.00,
                'stock': 40,
                'description': 'Senzor de presiune absolută cu semnal analog 0-5V și interval de până la 700 kPa. Integrează un element piezorezistiv compensat termic. Ideal pentru măsurarea presiunii aerului în sisteme pneumatice și compresoare. Ieșirea analogică permite conectarea directă la ADC.',
                'platforms': ['arduino-uno', 'arduino-mega', 'stm32'],
                'attrs': {
                    'pressure_range': (0, 7),
                    'accuracy': 2.5,
                    'pressure_type': 'Absolută',
                    'output_signal': '0-5V',
                    'supply_voltage': 5.0,
                    'media_compatible': 'Aer',
                }
            },
            {
                'name': 'BMP280 Senzor presiune barometrică I2C',
                'slug': 'bmp280-barometric-i2c',
                'sku': 'PRS-00002',
                'manufacturer': 'Bosch',
                'price': 15.00,
                'stock': 100,
                'description': 'Senzor digital de presiune barometrică de înaltă precizie cu interfață I2C/SPI. Rezoluția de 0.12 hPa permite măsurarea variațiilor de altitudine de sub 1 metru. Perfect pentru stații meteo, drone și echipamente de navigație. Consum foarte redus de energie.',
                'platforms': ['arduino-uno', 'esp8266', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'pressure_range': (0.3, 1.1),
                    'accuracy': 0.12,
                    'pressure_type': 'Absolută',
                    'output_signal': 'I2C',
                    'supply_voltage': 3.3,
                    'media_compatible': 'Aer',
                }
            },
            {
                'name': 'AMS 5812 Senzor presiune diferențială',
                'slug': 'ams5812-differential',
                'sku': 'PRS-00003',
                'manufacturer': 'Analog Microelectronics',
                'price': 185.00,
                'stock': 15,
                'description': 'Senzor de presiune diferențială de precizie ridicată cu compensare digitală integrată. Intervalul de 0-4 bar și comunicarea I2C îl fac ideal pentru filtre, ventilatoare HVAC și sisteme de flux de aer. Calibrat digital individual în fabrică pentru precizie maximă.',
                'platforms': ['arduino-mega', 'stm32'],
                'attrs': {
                    'pressure_range': (0, 4),
                    'accuracy': 0.5,
                    'pressure_type': 'Diferențială',
                    'output_signal': 'I2C',
                    'supply_voltage': 5.0,
                    'media_compatible': 'Aer',
                }
            },
            {
                'name': 'Sensata 60CP Transmițător presiune industrial',
                'slug': 'sensata-60cp-industrial',
                'sku': 'PRS-00004',
                'manufacturer': 'Sensata',
                'price': 320.00,
                'stock': 12,
                'description': 'Transmițător de presiune industrial cu ieșire 4-20mA și interval de 0-10 bar. Construit cu membrane din oțel inoxidabil 316L, rezistent la uleiuri și lichide agresive. Protecție IP67 și conexiune M12. Ideal pentru automatizarea proceselor din industria alimentară și chimică.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'pressure_range': (0, 10),
                    'accuracy': 0.5,
                    'pressure_type': 'Relativă',
                    'output_signal': '4-20mA',
                    'supply_voltage': 24.0,
                    'media_compatible': 'Ulei',
                }
            },
            {
                'name': 'XGZP6847 Senzor presiune lichide low-cost',
                'slug': 'xgzp6847-liquid-pressure',
                'sku': 'PRS-00005',
                'manufacturer': 'CFSensor',
                'price': 45.00,
                'stock': 60,
                'description': 'Senzor de presiune compact pentru măsurarea presiunii lichidelor cu ieșire I2C. Intervalul de 0-2 bar și dimensiunea redusă îl fac potrivit pentru sisteme de irigare, filtre de apă și monitorizarea presiunii în instalații sanitare. Raport calitate-preț excelent.',
                'platforms': ['arduino-uno', 'esp32', 'stm32'],
                'attrs': {
                    'pressure_range': (0, 2),
                    'accuracy': 1.0,
                    'pressure_type': 'Relativă',
                    'output_signal': 'I2C',
                    'supply_voltage': 3.3,
                    'media_compatible': 'Apă',
                }
            },
            {
                'name': 'MS5803-14BA Senzor presiune submersibil',
                'slug': 'ms5803-14ba-submersible',
                'sku': 'PRS-00006',
                'manufacturer': 'TE Connectivity',
                'price': 95.00,
                'stock': 25,
                'description': 'Senzor de presiune submersibil cu precizie ridicată și compensare de temperatură. Măsoară presiunea absolută până la 14 bar, echivalent cu aproximativ 140 metri adâncime de apă. Ideal pentru ROV-uri, scufundări și monitorizarea nivelului apei în puțuri.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'pressure_range': (0, 14),
                    'accuracy': 0.2,
                    'pressure_type': 'Absolută',
                    'output_signal': 'I2C',
                    'supply_voltage': 3.3,
                    'media_compatible': 'Apă',
                }
            },
        ]
        for prod in products:
            self._make_product(cat, prod, p)

    # ---------- Proximity Sensors ----------
    def _seed_proximity_sensors(self, p):
        cat = 'proximity-sensors'
        products = [
            {
                'name': 'LJ12A3-4-Z/BX Senzor inductiv M12',
                'slug': 'lj12a3-inductive-m12',
                'sku': 'PRX-00001',
                'manufacturer': 'Fotek',
                'price': 28.00,
                'stock': 70,
                'description': 'Senzor de proximitate inductiv M12 cu distanță de detecție de 4mm și ieșire PNP NO. Detectează obiecte metalice feroase la viteze mari de comutare. Corp cilindric din alamă nichelată cu protecție IP67 pentru medii industriale dure.',
                'platforms': ['plc-siemens-s7', 'arduino-mega'],
                'attrs': {
                    'detect_distance': 4.0,
                    'sensor_type': 'Inductiv',
                    'output_type': 'PNP NO',
                    'supply_voltage': (6, 36),
                    'switch_freq': 1500.0,
                    'ip_rating': 'IP67',
                }
            },
            {
                'name': 'E18-D80NK Senzor optic reflectiv ajustabil',
                'slug': 'e18-d80nk-optical',
                'sku': 'PRX-00002',
                'manufacturer': 'Elecrow',
                'price': 16.50,
                'stock': 90,
                'description': 'Senzor fotoelectric infraroșu cu distanță de detecție ajustabilă 3-80mm. Ieșire NPN compatibilă cu microcontrolere 5V. Potrivit pentru detectarea obiectelor pe linii de producție, roboți line-follower și numărătoare de piese.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32'],
                'attrs': {
                    'detect_distance': 80.0,
                    'sensor_type': 'Optic',
                    'output_type': 'NPN NO',
                    'supply_voltage': (5, 5),
                    'switch_freq': 100.0,
                    'ip_rating': 'IP54',
                }
            },
            {
                'name': 'HC-SR505 Senzor PIR mini prezență',
                'slug': 'hc-sr505-pir-mini',
                'sku': 'PRX-00003',
                'manufacturer': 'OSEPP',
                'price': 9.00,
                'stock': 100,
                'description': 'Senzor PIR miniaturizat pentru detectarea prezenței umane pe o rază de până la 3 metri. Dimensiunea compactă și consumul redus îl fac ideal pentru proiecte IoT de automatizare a iluminatului, sisteme de securitate și detectoare de prezență alimentate pe baterii.',
                'platforms': ['arduino-uno', 'esp8266', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'detect_distance': 3000.0,
                    'sensor_type': 'Optic',
                    'output_type': 'PNP NO',
                    'supply_voltage': (4.5, 20),
                    'switch_freq': 50.0,
                    'ip_rating': 'IP20',
                }
            },
            {
                'name': 'CR18-8DN Senzor capacitiv M18',
                'slug': 'cr18-8dn-capacitive-m18',
                'sku': 'PRX-00004',
                'manufacturer': 'Autonics',
                'price': 65.00,
                'stock': 35,
                'description': 'Senzor de proximitate capacitiv M18 pentru detectarea materialelor nemetalice precum plastic, lichide și cereale. Distanță de detecție de 8mm, ieșire NPN NO. Protecția IP67 permite montarea în medii cu praf și umiditate.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'detect_distance': 8.0,
                    'sensor_type': 'Capacitiv',
                    'output_type': 'NPN NO',
                    'supply_voltage': (12, 24),
                    'switch_freq': 500.0,
                    'ip_rating': 'IP67',
                }
            },
            {
                'name': 'Reed Switch MC-38 Senzor magnetic ușă/fereastră',
                'slug': 'mc38-reed-switch-magnetic',
                'sku': 'PRX-00005',
                'manufacturer': 'Generic',
                'price': 5.50,
                'stock': 100,
                'description': 'Senzor magnetic tip reed switch pentru detectarea deschiderii ușilor și ferestrelor. Contactul se închide când magnetul este la mai puțin de 15mm. Ideal pentru sisteme de alarmă, automatizări casnice și proiecte de securitate smart home.',
                'platforms': ['arduino-uno', 'esp8266', 'esp32', 'raspberry-pi', 'microbit'],
                'attrs': {
                    'detect_distance': 15.0,
                    'sensor_type': 'Magnetic',
                    'output_type': 'Push-Pull',
                    'supply_voltage': (5, 100),
                    'switch_freq': 200.0,
                    'ip_rating': 'IP20',
                }
            },
            {
                'name': 'SICK WT100-P330 Senzor fotoelectric industrial',
                'slug': 'sick-wt100-p330-photoelectric',
                'sku': 'PRX-00006',
                'manufacturer': 'SICK',
                'price': 380.00,
                'stock': 10,
                'description': 'Senzor fotoelectric de performanță industrială cu distanță de detecție de până la 1 metru. Fascicul optic vizibil red point pentru aliniere ușoară. Ieșire PNP NO, protecție IP67 și conector M8. Folosit pe liniile de producție auto și ambalare.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'detect_distance': 1000.0,
                    'sensor_type': 'Optic',
                    'output_type': 'PNP NO',
                    'supply_voltage': (10, 30),
                    'switch_freq': 1000.0,
                    'ip_rating': 'IP67',
                }
            },
        ]
        for prod in products:
            self._make_product(cat, prod, p)

    # ---------- Motion Sensors ----------
    def _seed_motion_sensors(self, p):
        cat = 'motion-sensors'
        products = [
            {
                'name': 'HC-SR501 Senzor PIR detecție mișcare',
                'slug': 'hc-sr501-pir-motion',
                'sku': 'MOT-00001',
                'manufacturer': 'BISS0001',
                'price': 7.50,
                'stock': 100,
                'description': 'Senzor PIR clasic pentru detectarea mișcării persoanelor cu rază de până la 7 metri și unghi de 120°. Sensibilitatea și timpul de întârziere sunt ajustabile prin potențiometre. Cel mai popular senzor de mișcare pentru proiecte Arduino și automatizări casnice.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp8266', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'detection_angle': 120.0,
                    'detect_distance': 7.0,
                    'sensor_type': 'PIR',
                    'supply_voltage': (5, 20),
                    'delay_time': (0.3, 200),
                }
            },
            {
                'name': 'AM312 Senzor PIR miniaturizat 3V',
                'slug': 'am312-pir-mini-3v',
                'sku': 'MOT-00002',
                'manufacturer': 'Senba',
                'price': 6.00,
                'stock': 80,
                'description': 'Senzor PIR miniaturizat cu consum ultra-redus, funcționând de la 2.7V. Raza de detecție de 3 metri cu unghi de 100°. Dimensiunea de doar 10x10mm permite integrarea în cele mai compacte proiecte IoT alimentate pe baterii sau celule solare.',
                'platforms': ['esp8266', 'esp32', 'stm32', 'microbit'],
                'attrs': {
                    'detection_angle': 100.0,
                    'detect_distance': 3.0,
                    'sensor_type': 'PIR',
                    'supply_voltage': (2.7, 12),
                    'delay_time': (2, 2),
                }
            },
            {
                'name': 'MPU6050 Accelerometru și giroscop 6 axe',
                'slug': 'mpu6050-6axis-imu',
                'sku': 'MOT-00003',
                'manufacturer': 'InvenSense',
                'price': 14.00,
                'stock': 75,
                'description': 'Modul IMU cu 6 axe (accelerometru 3 axe + giroscop 3 axe) cu interfață I2C. Procesorul DMP integrat calculează orientarea fără sarcină suplimentară pe microcontroler. Esențial pentru roboți de echilibru, drone, controlere de joc și trackere de mișcare.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'detection_angle': 360.0,
                    'detect_distance': 0.0,
                    'sensor_type': 'Dual PIR+Microundă',
                    'supply_voltage': (3.3, 3.3),
                    'delay_time': (1, 1),
                }
            },
            {
                'name': 'ADXL345 Accelerometru digital 3 axe',
                'slug': 'adxl345-3axis-accelerometer',
                'sku': 'MOT-00004',
                'manufacturer': 'Analog Devices',
                'price': 18.00,
                'stock': 60,
                'description': 'Accelerometru digital MEMS de 3 axe cu rezoluție de 13 biți și sensibilitate selectabilă ±2g/±4g/±8g/±16g. Funcții integrate de detecție tap/double-tap, free-fall și activitate/inactivitate. Comunicare I2C sau SPI. Consum foarte redus de doar 25μA.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'detection_angle': 360.0,
                    'detect_distance': 0.0,
                    'sensor_type': 'Dual PIR+Microundă',
                    'supply_voltage': (2.0, 3.6),
                    'delay_time': (1, 1),
                }
            },
            {
                'name': 'RCWL-0516 Senzor mișcare microunde',
                'slug': 'rcwl-0516-microwave-motion',
                'sku': 'MOT-00005',
                'manufacturer': 'RCWL',
                'price': 11.00,
                'stock': 65,
                'description': 'Senzor de mișcare bazat pe radar Doppler cu microunde care detectează mișcarea prin pereți subțiri, sticlă și plastic. Raza de detecție de 7 metri cu acoperire de 360°. Nu necesită vizibilitate directă ca senzorii PIR, oferind flexibilitate în montaj.',
                'platforms': ['arduino-uno', 'esp8266', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'detection_angle': 360.0,
                    'detect_distance': 7.0,
                    'sensor_type': 'Microundă',
                    'supply_voltage': (4, 28),
                    'delay_time': (2, 10),
                }
            },
        ]
        for prod in products:
            self._make_product(cat, prod, p)

    # ---------- Gas Sensors ----------
    def _seed_gas_sensors(self, p):
        cat = 'gas-sensors'
        products = [
            {
                'name': 'MQ-2 Senzor gaz combustibil și fum',
                'slug': 'mq2-combustible-gas-smoke',
                'sku': 'GAS-00001',
                'manufacturer': 'Hanwei',
                'price': 13.00,
                'stock': 90,
                'description': 'Senzor analogic pentru detectarea gazelor combustibile (GPL, metan, propan) și fumului. Elementul sensibil din SnO2 oferă un semnal proporțional cu concentrația gazului. Necesită o perioadă de preîncălzire de 20 secunde. Utilizat în sisteme de alarmă gaz pentru locuințe.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32'],
                'attrs': {
                    'gas_type': 'CH4/GPL',
                    'ppm_range': (200, 10000),
                    'warmup_time': 20.0,
                    'supply_voltage': 5.0,
                    'output_type': 'Analog',
                }
            },
            {
                'name': 'MQ-7 Senzor monoxid de carbon CO',
                'slug': 'mq7-carbon-monoxide',
                'sku': 'GAS-00002',
                'manufacturer': 'Hanwei',
                'price': 14.50,
                'stock': 70,
                'description': 'Senzor electrochimic pentru detectarea monoxidului de carbon (CO) în gama 20-2000 ppm. Funcționează cu cicluri alternante de tensiune ridicată și joasă. Esențial pentru detectarea scurgerilor de CO din centralele termice, șemineuri și garaje.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32', 'stm32'],
                'attrs': {
                    'gas_type': 'CO',
                    'ppm_range': (20, 2000),
                    'warmup_time': 60.0,
                    'supply_voltage': 5.0,
                    'output_type': 'Analog',
                }
            },
            {
                'name': 'MQ-135 Senzor calitate aer multi-gaz',
                'slug': 'mq135-air-quality',
                'sku': 'GAS-00003',
                'manufacturer': 'Hanwei',
                'price': 12.00,
                'stock': 85,
                'description': 'Senzor pentru monitorizarea calității aerului cu sensibilitate la NH3, NOx, alcool, benzen și fum. Ieșire analogică proporțională cu concentrația poluanților. Ideal pentru sisteme de ventilație inteligentă și monitorizare a calității aerului interior.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32'],
                'attrs': {
                    'gas_type': 'NH3',
                    'ppm_range': (10, 300),
                    'warmup_time': 20.0,
                    'supply_voltage': 5.0,
                    'output_type': 'Analog',
                }
            },
            {
                'name': 'CCS811 Senzor CO2 și VOC digital I2C',
                'slug': 'ccs811-co2-voc-digital',
                'sku': 'GAS-00004',
                'manufacturer': 'ScioSense',
                'price': 42.00,
                'stock': 40,
                'description': 'Senzor digital pentru eCO2 și compuși organici volatili (TVOC) cu interfață I2C. Măsoară eCO2 în gama 400-8192 ppm și TVOC 0-1187 ppb. Procesare on-chip integrată, nu necesită calcule suplimentare pe microcontroler. Perfect pentru smart home și monitorizare birou.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'gas_type': 'VOC',
                    'ppm_range': (400, 8192),
                    'warmup_time': 60.0,
                    'supply_voltage': 3.3,
                    'output_type': 'I2C',
                }
            },
            {
                'name': 'SGP30 Senzor VOC și CO2 echivalent Sensirion',
                'slug': 'sgp30-voc-eco2',
                'sku': 'GAS-00005',
                'manufacturer': 'Sensirion',
                'price': 55.00,
                'stock': 30,
                'description': 'Senzor multi-pixel de gaze cu algoritm on-chip pentru TVOC și CO2 echivalent. Compensare automată a umidității și linie de bază adaptivă. Timp de încălzire de doar 15 secunde. Ideal pentru purificatoare de aer inteligente și sisteme HVAC.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'gas_type': 'VOC',
                    'ppm_range': (0, 60000),
                    'warmup_time': 15.0,
                    'supply_voltage': 3.3,
                    'output_type': 'I2C',
                }
            },
            {
                'name': 'SCD40 Senzor CO2 fotoacustic real',
                'slug': 'scd40-true-co2-photoacoustic',
                'sku': 'GAS-00006',
                'manufacturer': 'Sensirion',
                'price': 145.00,
                'stock': 15,
                'description': 'Senzor de CO2 adevărat (nu estimat) bazat pe principiul fotoacustic NDIR. Măsoară CO2 real în gama 400-2000 ppm cu o precizie de ±40 ppm. Include și senzori de temperatură și umiditate. Dimensiuni miniaturizate de doar 10x10x7mm.',
                'platforms': ['esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'gas_type': 'CO2',
                    'ppm_range': (400, 2000),
                    'warmup_time': 0.0,
                    'supply_voltage': 3.3,
                    'output_type': 'I2C',
                }
            },
        ]
        for prod in products:
            self._make_product(cat, prod, p)

    # ---------- Humidity Sensors ----------
    def _seed_humidity_sensors(self, p):
        cat = 'humidity-sensors'
        products = [
            {
                'name': 'DHT11 Senzor umiditate și temperatură basic',
                'slug': 'dht11-humidity-basic',
                'sku': 'HUM-00001',
                'manufacturer': 'Aosong',
                'price': 7.00,
                'stock': 100,
                'description': 'Senzor economic de umiditate și temperatură cu ieșire digitală. Precizie de ±5%RH în gama 20-80% și ±2°C pentru temperatură. Soluție ideală pentru proiecte educaționale și aplicații unde precizia ridicată nu este critică.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp8266', 'esp32', 'raspberry-pi', 'microbit'],
                'attrs': {
                    'humidity_range': (20, 80),
                    'humidity_acc': 5.0,
                    'temp_range': (0, 50),
                    'interface': 'Digital',
                    'sensor_type': 'Capacitiv',
                }
            },
            {
                'name': 'SHT40 Senzor umiditate precizie Sensirion',
                'slug': 'sht40-precision-humidity',
                'sku': 'HUM-00002',
                'manufacturer': 'Sensirion',
                'price': 38.00,
                'stock': 45,
                'description': 'Senzor digital de umiditate de generație nouă cu precizie de ±1.8%RH și interfață I2C. Dimensiunea ultra-compactă de 1.5x1.5mm și consumul redus îl fac ideal pentru dispozitive wearable, IoT și echipamente medicale portabile.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'humidity_range': (0, 100),
                    'humidity_acc': 1.8,
                    'temp_range': (-40, 125),
                    'interface': 'I2C',
                    'sensor_type': 'Capacitiv',
                }
            },
            {
                'name': 'HIH-4030 Senzor umiditate analog Honeywell',
                'slug': 'hih4030-analog-humidity',
                'sku': 'HUM-00003',
                'manufacturer': 'Honeywell',
                'price': 55.00,
                'stock': 25,
                'description': 'Senzor analogic de umiditate cu ieșire liniară în tensiune. Precizia de ±3.5%RH și timpul de răspuns rapid de 5 secunde. Funcționare stabilă pe termen lung cu drift minim. Potrivit pentru sisteme HVAC și control climatic în sere.',
                'platforms': ['arduino-uno', 'arduino-mega', 'stm32'],
                'attrs': {
                    'humidity_range': (0, 100),
                    'humidity_acc': 3.5,
                    'temp_range': (-40, 85),
                    'interface': 'Analog',
                    'sensor_type': 'Capacitiv',
                }
            },
            {
                'name': 'AM2320 Senzor umiditate I2C compact',
                'slug': 'am2320-i2c-humidity',
                'sku': 'HUM-00004',
                'manufacturer': 'Aosong',
                'price': 12.00,
                'stock': 80,
                'description': 'Senzor digital compact de umiditate și temperatură cu interfață I2C. Precizie de ±3%RH și interval de 0-99.9%RH. Format DFN mic, potrivit pentru integrarea pe PCB-uri compacte. Funcționare pe 3.3V sau 5V.',
                'platforms': ['arduino-uno', 'esp8266', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'humidity_range': (0, 99.9),
                    'humidity_acc': 3.0,
                    'temp_range': (-40, 80),
                    'interface': 'I2C',
                    'sensor_type': 'Capacitiv',
                }
            },
        ]
        for prod in products:
            self._make_product(cat, prod, p)

    # ---------- Distance Sensors ----------
    def _seed_distance_sensors(self, p):
        cat = 'distance-sensors'
        products = [
            {
                'name': 'HC-SR04 Senzor ultrasonic distanță',
                'slug': 'hc-sr04-ultrasonic-distance',
                'sku': 'DST-00001',
                'manufacturer': 'Generic',
                'price': 8.00,
                'stock': 100,
                'description': 'Cel mai popular senzor ultrasonic de distanță cu interval de 2-400cm. Funcționează pe principiul ecou - emite un puls ultrasonic și măsoară timpul de întoarcere. Ideal pentru roboți evită-obstacole, parcări inteligente și sisteme de nivel lichid.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp8266', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'measure_range': (2, 400),
                    'accuracy': 3.0,
                    'technology': 'Ultrasonic',
                    'beam_angle': 15.0,
                    'supply_voltage': 5.0,
                    'interface': 'GPIO Digital',
                }
            },
            {
                'name': 'VL53L0X Senzor distanță laser ToF I2C',
                'slug': 'vl53l0x-laser-tof',
                'sku': 'DST-00002',
                'manufacturer': 'STMicroelectronics',
                'price': 22.00,
                'stock': 75,
                'description': 'Senzor Time-of-Flight cu laser VCSEL pentru măsurarea distanțelor cu precizie de 1mm. Intervalul de 3-200cm și interfața I2C permit integrarea rapidă. Nu este afectat de culoarea sau reflectivitatea suprafeței. Ideal pentru dronele indoor și roboți.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'measure_range': (3, 200),
                    'accuracy': 1.0,
                    'technology': 'Laser ToF',
                    'beam_angle': 25.0,
                    'supply_voltage': 3.3,
                    'interface': 'I2C',
                }
            },
            {
                'name': 'GP2Y0A21YK0F Senzor IR distanță Sharp',
                'slug': 'sharp-gp2y0a21-ir-distance',
                'sku': 'DST-00003',
                'manufacturer': 'Sharp',
                'price': 28.00,
                'stock': 50,
                'description': 'Senzor infraroșu de distanță cu ieșire analogică proporțională cu distanța. Intervalul de 10-80cm cu fascicul focalizat de doar 5°. Foarte rapid (timp de citire sub 40ms), potrivit pentru aplicații de evitare a obstacolelor pe roboți rapizi.',
                'platforms': ['arduino-uno', 'arduino-mega', 'stm32'],
                'attrs': {
                    'measure_range': (10, 80),
                    'accuracy': 3.0,
                    'technology': 'Infraroșu',
                    'beam_angle': 5.0,
                    'supply_voltage': 5.0,
                    'interface': 'Analog',
                }
            },
            {
                'name': 'JSN-SR04T Senzor ultrasonic waterproof',
                'slug': 'jsn-sr04t-ultrasonic-waterproof',
                'sku': 'DST-00004',
                'manufacturer': 'Generic',
                'price': 24.00,
                'stock': 55,
                'description': 'Senzor ultrasonic waterproof cu transductor separat rezistent la apă. Interval de 20-600cm, potrivit pentru măsurarea nivelului de lichid în rezervoare, sisteme de irigare și aplicații outdoor. Cablu de 2.5m între modul și transductor.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32'],
                'attrs': {
                    'measure_range': (20, 600),
                    'accuracy': 2.0,
                    'technology': 'Ultrasonic',
                    'beam_angle': 60.0,
                    'supply_voltage': 5.0,
                    'interface': 'GPIO Digital',
                }
            },
            {
                'name': 'TFmini-S LiDAR Senzor distanță laser',
                'slug': 'tfmini-s-lidar-distance',
                'sku': 'DST-00005',
                'manufacturer': 'Benewake',
                'price': 185.00,
                'stock': 18,
                'description': 'Senzor LiDAR miniaturizat cu interval de măsurare de 10cm la 12m și frecvență de scanare de 100Hz. Comunicare UART la 115200 baud. Greutate de doar 5g, ideal pentru drone, roboți autonomi și sisteme de cartografiere. Performanță excelentă în lumină puternică.',
                'platforms': ['arduino-mega', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'measure_range': (10, 1200),
                    'accuracy': 1.0,
                    'technology': 'LIDAR',
                    'beam_angle': 2.3,
                    'supply_voltage': 5.0,
                    'interface': 'UART',
                }
            },
        ]
        for prod in products:
            self._make_product(cat, prod, p)

    # ---------- Light Sensors ----------
    def _seed_light_sensors(self, p):
        cat = 'light-sensors'
        products = [
            {
                'name': 'BH1750 Senzor lumină ambientală I2C',
                'slug': 'bh1750-ambient-light',
                'sku': 'LGT-00001',
                'manufacturer': 'ROHM',
                'price': 10.00,
                'stock': 85,
                'description': 'Senzor digital de lumină ambientală cu ieșire directă în lux prin I2C. Interval de 1-65535 lux cu rezoluție de 1 lux. Nu necesită calibrare sau calcule suplimentare. Ideal pentru reglarea automată a luminozității ecranelor și iluminatului.',
                'platforms': ['arduino-uno', 'esp8266', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'lux_range': (1, 65535),
                    'spectrum': 'Vizibil',
                    'interface': 'I2C',
                    'supply_voltage': 3.3,
                }
            },
            {
                'name': 'TSL2591 Senzor lumină spectru complet',
                'slug': 'tsl2591-full-spectrum-light',
                'sku': 'LGT-00002',
                'manufacturer': 'AMS-OSRAM',
                'price': 25.00,
                'stock': 40,
                'description': 'Senzor de lumină cu gamă dinamică extinsă de 188 micro-lux la 88000 lux. Două fotodiode separate pentru lumină vizibilă și infraroșu complet. Câștig și timp de integrare configurabile prin I2C. Potrivit pentru sisteme de automatizare a iluminatului.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'lux_range': (0.001, 88000),
                    'spectrum': 'Full spectrum',
                    'interface': 'I2C',
                    'supply_voltage': 3.3,
                }
            },
            {
                'name': 'VEML6075 Senzor UV UVA/UVB I2C',
                'slug': 'veml6075-uv-sensor',
                'sku': 'LGT-00003',
                'manufacturer': 'Vishay',
                'price': 18.00,
                'stock': 35,
                'description': 'Senzor ultraviolet care măsoară separat radiația UVA (365nm) și UVB (330nm). Calculează indexul UV conform standardului CIE. Comunicare I2C simplă. Folosit în stații meteo, dispozitive de monitorizare a expunerii solare și dozimetre UV.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'lux_range': (0, 10000),
                    'spectrum': 'UV',
                    'interface': 'I2C',
                    'supply_voltage': 3.3,
                }
            },
            {
                'name': 'Fotorezistor GL5528 LDR 5mm',
                'slug': 'gl5528-ldr-photoresistor',
                'sku': 'LGT-00004',
                'manufacturer': 'Generic',
                'price': 2.00,
                'stock': 100,
                'description': 'Fotorezistor clasic din cadmiu sulfid cu diametrul de 5mm. Rezistența variază de la ~1kΩ (lumină) la ~10MΩ (întuneric). Soluția cea mai simplă și economică pentru detectarea luminii. Se conectează cu un simplu divisor de tensiune la intrarea analogică.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp8266', 'esp32', 'microbit'],
                'attrs': {
                    'lux_range': (1, 100000),
                    'spectrum': 'Vizibil',
                    'interface': 'Analog',
                    'supply_voltage': 5.0,
                }
            },
        ]
        for prod in products:
            self._make_product(cat, prod, p)

    # ---------- DC Motors ----------
    def _seed_dc_motors(self, p):
        cat = 'dc-motors'
        products = [
            {
                'name': 'Motor DC 6V cu reductor 1:48 și roată',
                'slug': 'dc-motor-6v-gearbox-148',
                'sku': 'DCM-00001',
                'manufacturer': 'Generic',
                'price': 12.00,
                'stock': 100,
                'description': 'Motor DC de 6V cu reductor plastic raport 1:48, potrivit pentru roboți cu roți și mașinuțe RC. Include roată de 65mm. Turație de ~200 RPM la sarcină zero. Cel mai utilizat motor pentru proiecte robotice educaționale și competiții.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'voltage': 6.0,
                    'current': 0.2,
                    'rpm': 200.0,
                    'power': 1.2,
                    'motor_type': 'Motor DC cu reductor',
                }
            },
            {
                'name': 'Motor DC 12V 300RPM cu encoder Hall',
                'slug': 'dc-motor-12v-300rpm-encoder',
                'sku': 'DCM-00002',
                'manufacturer': 'JGA25-371',
                'price': 65.00,
                'stock': 35,
                'description': 'Motor DC de 12V cu reductor metalic și encoder Hall cu 11 impulsuri/rotație. Controlul precis al vitezei și poziției prin citirea encoder-ului. Turație de 300 RPM cu cuplu de 5 kg·cm. Ideal pentru roboți autonomi care necesită odometrie.',
                'platforms': ['arduino-mega', 'esp32', 'stm32'],
                'attrs': {
                    'voltage': 12.0,
                    'current': 0.5,
                    'rpm': 300.0,
                    'power': 6.0,
                    'motor_type': 'Motor DC cu encoder',
                }
            },
            {
                'name': 'Motor DC 775 12V mare putere',
                'slug': 'dc-motor-775-12v-high-power',
                'sku': 'DCM-00003',
                'manufacturer': 'Generic',
                'price': 32.00,
                'stock': 50,
                'description': 'Motor DC 775 de mare putere cu 12000 RPM la 12V. Arbore de 5mm și corp din oțel. Putere de 80W, ideal pentru mașini de găurit, proiecte CNC mici, polizoare și aplicații care necesită turație și putere ridicate.',
                'platforms': ['arduino-mega', 'stm32'],
                'attrs': {
                    'voltage': 12.0,
                    'current': 6.0,
                    'rpm': 12000.0,
                    'power': 80.0,
                    'motor_type': 'Motor DC simplu',
                }
            },
        ]
        for prod in products:
            self._make_product(cat, prod, p)

    # ---------- Servo Motors ----------
    def _seed_servo_motors(self, p):
        cat = 'servo-motors'
        products = [
            {
                'name': 'SG90 Micro Servo 9g 180°',
                'slug': 'sg90-micro-servo-9g',
                'sku': 'SRV-00001',
                'manufacturer': 'TowerPro',
                'price': 15.00,
                'stock': 100,
                'description': 'Micro servo de 9g cu angrenaje din plastic și rotație de 180°. Cuplul de 1.8 kg·cm la 4.8V este suficient pentru proiecte de robotică ușoară, pan-tilt camere și mecanisme de dispensare. Cel mai vândut servo pentru Arduino.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'supply_voltage': (4.8, 6.0),
                    'torque': 1.8,
                    'rotation_angle': 180.0,
                    'servo_type': 'Micro',
                }
            },
            {
                'name': 'MG996R Servo Standard Metal Gear 180°',
                'slug': 'mg996r-standard-metal-gear',
                'sku': 'SRV-00002',
                'manufacturer': 'TowerPro',
                'price': 38.00,
                'stock': 60,
                'description': 'Servo standard cu angrenaje metalice și cuplu de 9.4 kg·cm. Construcție robustă pentru brațe robotice, hexapozi și aplicații care solicită mecanismul. Corpul metalic asigură disiparea eficientă a căldurii în funcționare continuă.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32'],
                'attrs': {
                    'supply_voltage': (4.8, 7.2),
                    'torque': 9.4,
                    'rotation_angle': 180.0,
                    'servo_type': 'Standard',
                }
            },
            {
                'name': 'DS3218 Servo Digital 20kg Waterproof 270°',
                'slug': 'ds3218-digital-20kg-270',
                'sku': 'SRV-00003',
                'manufacturer': 'DSSERVO',
                'price': 85.00,
                'stock': 25,
                'description': 'Servo digital de mare cuplu (20 kg·cm) cu angrenaje metalice și carcasă waterproof. Rotație extinsă de 270° pentru articulații robotice avansate. Feedback de poziție precis prin control PWM digital. Potrivit pentru roboți humanoid și brațe industriale.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32', 'stm32'],
                'attrs': {
                    'supply_voltage': (4.8, 6.8),
                    'torque': 20.0,
                    'rotation_angle': 270.0,
                    'servo_type': 'Digital',
                }
            },
            {
                'name': 'FS90R Servo rotație continuă 360°',
                'slug': 'fs90r-continuous-rotation',
                'sku': 'SRV-00004',
                'manufacturer': 'Feetech',
                'price': 22.00,
                'stock': 70,
                'description': 'Micro servo cu rotație continuă de 360° pentru tracțiunea roboților cu roți. Controlul direcției și vitezei se face prin semnalul PWM. Greutate de doar 9g cu angrenaje din plastic. Ideal pentru roboți Sumo și line-follower.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'supply_voltage': (4.8, 6.0),
                    'torque': 1.5,
                    'rotation_angle': 360.0,
                    'servo_type': 'Continuu',
                }
            },
            {
                'name': 'MG90S Servo Mini Metal Gear 180°',
                'slug': 'mg90s-mini-metal-gear',
                'sku': 'SRV-00005',
                'manufacturer': 'TowerPro',
                'price': 20.00,
                'stock': 80,
                'description': 'Servo mini cu angrenaje metalice și greutate de doar 13.4g. Cuplul de 2.2 kg·cm oferă performanță superioară SG90 la dimensiuni similare. Potrivit pentru proiecte unde durabilitatea angrenajelor este importantă dar spațiul este limitat.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp8266', 'esp32'],
                'attrs': {
                    'supply_voltage': (4.8, 6.0),
                    'torque': 2.2,
                    'rotation_angle': 180.0,
                    'servo_type': 'Mini',
                }
            },
        ]
        for prod in products:
            self._make_product(cat, prod, p)

    # ---------- Stepper Motors ----------
    def _seed_stepper_motors(self, p):
        cat = 'stepper-motors'
        products = [
            {
                'name': 'NEMA17 Motor Pas cu Pas 1.8° 42mm',
                'slug': 'nema17-stepper-18deg-42mm',
                'sku': 'STP-00001',
                'manufacturer': 'Changzhou Fulling',
                'price': 52.00,
                'stock': 60,
                'description': 'Motor stepper NEMA17 standard cu unghi de pas de 1.8° (200 pași/rotație). Cuplu de retenție de 0.4 N·m și curent de 1.7A per fază. Cel mai utilizat stepper pentru imprimante 3D, CNC și mașini de gravat laser.',
                'platforms': ['arduino-mega', 'esp32', 'stm32'],
                'attrs': {
                    'step_angle': 1.8,
                    'current_phase': 1.7,
                    'holding_torque': 0.4,
                    'wire_count': 4,
                }
            },
            {
                'name': '28BYJ-48 Motor Pas cu Pas 5V cu driver ULN2003',
                'slug': '28byj48-stepper-5v-uln2003',
                'sku': 'STP-00002',
                'manufacturer': 'Generic',
                'price': 14.00,
                'stock': 100,
                'description': 'Motor stepper micro cu reductor intern (raport 1:64) și driver ULN2003 inclus. Funcționează la 5V direct de la Arduino, fără alimentare externă necesară. Cuplu mic dar suficient pentru proiecte simple de rotire, cadrane și mecanisme ușoare.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32', 'raspberry-pi', 'microbit'],
                'attrs': {
                    'step_angle': 5.625,
                    'current_phase': 0.2,
                    'holding_torque': 0.03,
                    'wire_count': 4,
                }
            },
            {
                'name': 'NEMA23 Motor Pas cu Pas 2.8A',
                'slug': 'nema23-stepper-28a',
                'sku': 'STP-00003',
                'manufacturer': 'Changzhou Fulling',
                'price': 95.00,
                'stock': 30,
                'description': 'Motor stepper NEMA23 de putere medie cu cuplu de retenție de 1.26 N·m. Curent de 2.8A per fază necesită un driver dedicat (TB6600 sau DM542). Potrivit pentru routere CNC, mașini de tăiat plasmă și echipamente industriale de precizie.',
                'platforms': ['stm32', 'plc-siemens-s7'],
                'attrs': {
                    'step_angle': 1.8,
                    'current_phase': 2.8,
                    'holding_torque': 1.26,
                    'wire_count': 4,
                }
            },
        ]
        for prod in products:
            self._make_product(cat, prod, p)

    # ---------- Relays ----------
    def _seed_relays(self, p):
        cat = 'relays'
        products = [
            {
                'name': 'Modul Releu 5V 1 Canal cu optocuplor',
                'slug': 'relay-module-5v-1ch-optocoupler',
                'sku': 'RLY-00001',
                'manufacturer': 'SRD',
                'price': 8.00,
                'stock': 100,
                'description': 'Modul releu cu un canal, alimentat la 5V cu izolare optică prin optocuplor. Comută sarcini de până la 10A la 250V AC. LED indicator de stare și protecție flyback diodă. Cel mai simplu mod de a controla aparate electrocasnice cu Arduino.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'coil_voltage': 5.0,
                    'max_current': 10.0,
                    'max_voltage_ac': 250.0,
                    'relay_type': 'Electromecanic',
                }
            },
            {
                'name': 'Modul Releu 12V 4 Canale cu optocuplor',
                'slug': 'relay-module-12v-4ch',
                'sku': 'RLY-00002',
                'manufacturer': 'Songle',
                'price': 22.00,
                'stock': 65,
                'description': 'Modul releu cu 4 canale independente, bobină de 12V și izolare optică. Fiecare canal comută până la 10A/250V AC cu contacte NO și NC. LED-uri individuale de stare. Ideal pentru automatizarea a 4 circuite separate (lumini, pompe, ventilatoare).',
                'platforms': ['arduino-mega', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'coil_voltage': 12.0,
                    'max_current': 10.0,
                    'max_voltage_ac': 250.0,
                    'relay_type': 'Electromecanic',
                }
            },
            {
                'name': 'SSR-25DA Releu Solid State 25A',
                'slug': 'ssr-25da-solid-state-25a',
                'sku': 'RLY-00003',
                'manufacturer': 'Fotek',
                'price': 35.00,
                'stock': 40,
                'description': 'Releu solid-state (SSR) pentru comutarea sarcinilor AC de până la 25A fără contacte mecanice. Activare cu semnal DC 3-32V, compatibil cu orice microcontroler. Fără zgomot de comutare, durată de viață nelimitată. Necesită radiator la curenți peste 10A.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'plc-siemens-s7'],
                'attrs': {
                    'coil_voltage': 3.0,
                    'max_current': 25.0,
                    'max_voltage_ac': 380.0,
                    'relay_type': 'SSR (Solid State)',
                }
            },
            {
                'name': 'Modul Releu 5V 8 Canale',
                'slug': 'relay-module-5v-8ch',
                'sku': 'RLY-00004',
                'manufacturer': 'SRD',
                'price': 32.00,
                'stock': 45,
                'description': 'Modul releu cu 8 canale la 5V pentru automatizare complexă. Fiecare canal cu izolare optică, LED indicator și protecție. Comutare 10A/250V AC per canal. Perfect pentru sisteme de automatizare casnice cu mai multe zone de iluminat sau echipamente.',
                'platforms': ['arduino-mega', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'coil_voltage': 5.0,
                    'max_current': 10.0,
                    'max_voltage_ac': 250.0,
                    'relay_type': 'Electromecanic',
                }
            },
        ]
        for prod in products:
            self._make_product(cat, prod, p)

    # ---------- Arduino Boards ----------
    def _seed_arduino_boards(self, p):
        cat = 'arduino-boards'
        products = [
            {
                'name': 'Arduino Uno R3 ATmega328P Original',
                'slug': 'arduino-uno-r3-original',
                'sku': 'ARD-00001',
                'manufacturer': 'Arduino',
                'price': 89.00,
                'stock': 50,
                'description': 'Placa de dezvoltare Arduino Uno R3 originală cu microcontrolerul ATmega328P. 14 pini digitali (6 PWM), 6 intrări analogice și memorie Flash de 32KB. Platforma standard pentru învățarea electronică, cu cea mai mare comunitate de suport și biblioteci.',
                'platforms': ['arduino-uno'],
                'attrs': {
                    'mcu': 'ATmega328P',
                    'operating_voltage': 5.0,
                    'digital_pins': 14,
                    'analog_pins': 6,
                    'flash_memory': 32,
                    'clock_freq': 16.0,
                    'connectivity': 'Fără',
                }
            },
            {
                'name': 'Arduino Mega 2560 R3',
                'slug': 'arduino-mega-2560-r3',
                'sku': 'ARD-00002',
                'manufacturer': 'Arduino',
                'price': 145.00,
                'stock': 35,
                'description': 'Placa Arduino Mega cu ATmega2560 oferind 54 pini digitali, 16 intrări analogice și 256KB Flash. Ideală pentru proiecte complexe cu multe periferice: imprimante 3D, CNC, roboți multi-senzor și sisteme de automatizare cu multe I/O-uri simultane.',
                'platforms': ['arduino-mega'],
                'attrs': {
                    'mcu': 'ATmega2560',
                    'operating_voltage': 5.0,
                    'digital_pins': 54,
                    'analog_pins': 16,
                    'flash_memory': 256,
                    'clock_freq': 16.0,
                    'connectivity': 'Fără',
                }
            },
            {
                'name': 'Arduino Nano Every ATMega4809',
                'slug': 'arduino-nano-every-4809',
                'sku': 'ARD-00003',
                'manufacturer': 'Arduino',
                'price': 75.00,
                'stock': 55,
                'description': 'Versiunea actualizată a Arduino Nano cu ATMega4809, oferind 48KB Flash și 6KB RAM la frecvență de 20MHz. Formatul compact de breadboard-friendly cu 14 pini digitali. Perfectă pentru proiecte portabile și prototipuri rapide pe dimensiuni mici.',
                'platforms': ['arduino-uno'],
                'attrs': {
                    'mcu': 'ATMega4809',
                    'operating_voltage': 5.0,
                    'digital_pins': 14,
                    'analog_pins': 8,
                    'flash_memory': 48,
                    'clock_freq': 20.0,
                    'connectivity': 'Fără',
                }
            },
            {
                'name': 'Arduino Nano 33 IoT WiFi+BT',
                'slug': 'arduino-nano-33-iot',
                'sku': 'ARD-00004',
                'manufacturer': 'Arduino',
                'price': 135.00,
                'stock': 30,
                'description': 'Arduino Nano cu modul WiFi și Bluetooth integrat bazat pe SAMD21. Funcționare la 3.3V cu 256KB Flash și procesor ARM Cortex-M0+ la 48MHz. Include criptografie hardware pentru conexiuni IoT securizate. Ideală pentru proiecte connected cu cloud.',
                'platforms': ['arduino-uno', 'esp32'],
                'attrs': {
                    'mcu': 'SAMD21',
                    'operating_voltage': 3.3,
                    'digital_pins': 14,
                    'analog_pins': 8,
                    'flash_memory': 256,
                    'clock_freq': 48.0,
                    'connectivity': 'WiFi+Bluetooth',
                }
            },
            {
                'name': 'Arduino MKR WiFi 1010',
                'slug': 'arduino-mkr-wifi-1010',
                'sku': 'ARD-00005',
                'manufacturer': 'Arduino',
                'price': 195.00,
                'stock': 20,
                'description': 'Placă din seria MKR cu WiFi și Bluetooth, proiectată pentru proiecte IoT profesionale. Procesor SAMD21 cu 256KB Flash, format compact cu conector baterie LiPo integrat. Suportă SSL/TLS nativ pentru comunicații securizate cu platforme cloud.',
                'platforms': ['arduino-uno'],
                'attrs': {
                    'mcu': 'SAMD21',
                    'operating_voltage': 3.3,
                    'digital_pins': 8,
                    'analog_pins': 7,
                    'flash_memory': 256,
                    'clock_freq': 48.0,
                    'connectivity': 'WiFi+Bluetooth',
                }
            },
        ]
        for prod in products:
            self._make_product(cat, prod, p)

    # ---------- ESP Boards ----------
    def _seed_esp_boards(self, p):
        cat = 'esp-boards'
        products = [
            {
                'name': 'ESP32 DevKit V1 WiFi+BT+BLE',
                'slug': 'esp32-devkit-v1-wifi-bt',
                'sku': 'ESP-00001',
                'manufacturer': 'Espressif',
                'price': 42.00,
                'stock': 80,
                'description': 'Placă de dezvoltare ESP32 cu dual-core Xtensa LX6 la 240MHz, WiFi, Bluetooth Classic și BLE. 30 pini GPIO, 4MB Flash și 520KB RAM. Cel mai popular modul IoT cu suport Arduino IDE, ESP-IDF și MicroPython.',
                'platforms': ['esp32'],
                'attrs': {
                    'main_chip': 'ESP32',
                    'flash_memory': 4,
                    'ram': 520,
                    'connectivity': 'WiFi+BT+BLE',
                    'gpio_pins': 30,
                    'supply_voltage': 3.3,
                }
            },
            {
                'name': 'ESP8266 NodeMCU V3 WiFi',
                'slug': 'esp8266-nodemcu-v3-wifi',
                'sku': 'ESP-00002',
                'manufacturer': 'LoLin',
                'price': 28.00,
                'stock': 100,
                'description': 'Modul ESP8266 în format NodeMCU cu port micro-USB și regulator integrat. WiFi 802.11 b/g/n, 4MB Flash și 80KB RAM. Programabil cu Arduino IDE sau Lua. Raport calitate-preț excelent pentru proiecte IoT simple cu conectivitate WiFi.',
                'platforms': ['esp8266'],
                'attrs': {
                    'main_chip': 'ESP8266',
                    'flash_memory': 4,
                    'ram': 80,
                    'connectivity': 'WiFi',
                    'gpio_pins': 11,
                    'supply_voltage': 3.3,
                }
            },
            {
                'name': 'ESP32-CAM Modul cu cameră OV2640',
                'slug': 'esp32-cam-ov2640-camera',
                'sku': 'ESP-00003',
                'manufacturer': 'AI-Thinker',
                'price': 55.00,
                'stock': 45,
                'description': 'Modul ESP32 cu cameră OV2640 de 2MP integrată și slot microSD. Streaming video prin WiFi, recunoaștere facială și captură foto. Alimentare la 5V. Ideal pentru supraveghere IoT, sonerii video inteligente și proiecte de computer vision.',
                'platforms': ['esp32'],
                'attrs': {
                    'main_chip': 'ESP32',
                    'flash_memory': 4,
                    'ram': 520,
                    'connectivity': 'WiFi+Bluetooth',
                    'gpio_pins': 9,
                    'supply_voltage': 5.0,
                }
            },
            {
                'name': 'ESP32-S3 DevKitC N8R8 WiFi+BLE',
                'slug': 'esp32-s3-devkitc-n8r8',
                'sku': 'ESP-00004',
                'manufacturer': 'Espressif',
                'price': 68.00,
                'stock': 35,
                'description': 'Cel mai avansat modul ESP32 cu procesor dual-core Xtensa LX7 și suport hardware AI/ML. 8MB Flash, 512KB SRAM și 8MB PSRAM pentru aplicații intensive. Suport nativ USB OTG. Ideal pentru edge computing, TinyML și interfețe utilizator complexe.',
                'platforms': ['esp32'],
                'attrs': {
                    'main_chip': 'ESP32-S3',
                    'flash_memory': 8,
                    'ram': 512,
                    'connectivity': 'WiFi+BT+BLE',
                    'gpio_pins': 36,
                    'supply_voltage': 3.3,
                }
            },
            {
                'name': 'WEMOS D1 Mini ESP8266 compact',
                'slug': 'wemos-d1-mini-esp8266',
                'sku': 'ESP-00005',
                'manufacturer': 'WEMOS',
                'price': 22.00,
                'stock': 100,
                'description': 'Cea mai compactă placă ESP8266 cu format de doar 34x25mm și pin header-e compatibile cu shield-urile WEMOS. WiFi integrat, 4MB Flash, port micro-USB. Ecosistem bogat de shield-uri stackable (releu, OLED, motor, baterie).',
                'platforms': ['esp8266', 'arduino-uno'],
                'attrs': {
                    'main_chip': 'ESP8266',
                    'flash_memory': 4,
                    'ram': 80,
                    'connectivity': 'WiFi',
                    'gpio_pins': 11,
                    'supply_voltage': 3.3,
                }
            },
        ]
        for prod in products:
            self._make_product(cat, prod, p)

    # ──────────────────────────────────────────────
    # USERS
    # ──────────────────────────────────────────────
    def _create_users(self):
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@autoshop.ro',
                'password': 'Admin1234!',
                'first_name': 'Admin',
                'last_name': 'AutoShop',
                'role': 'admin',
                'is_superuser': True,
            },
            {
                'username': 'ion.popescu',
                'email': 'ion.popescu@email.ro',
                'password': 'Test1234!',
                'first_name': 'Ion',
                'last_name': 'Popescu',
                'role': 'client',
            },
            {
                'username': 'maria.ionescu',
                'email': 'maria.ionescu@email.ro',
                'password': 'Test1234!',
                'first_name': 'Maria',
                'last_name': 'Ionescu',
                'role': 'client',
            },
        ]

        for u in users_data:
            is_super = u.pop('is_superuser', False)
            if not User.objects.filter(username=u['username']).exists():
                password = u.pop('password')
                if is_super:
                    User.objects.create_superuser(password=password, **u)
                else:
                    User.objects.create_user(password=password, **u)
                self.counts['users'] += 1
                self.stdout.write(f'  [OK] Created user: {u["email"]}')

    # ──────────────────────────────────────────────
    # SAMPLE ORDERS
    # ──────────────────────────────────────────────
    def _create_orders(self):
        try:
            ion = User.objects.get(username='ion.popescu')
            maria = User.objects.get(username='maria.ionescu')
        except User.DoesNotExist:
            return

        if Order.objects.filter(user=ion).exists():
            return

        all_products = list(Product.objects.all())
        sensors = [p for p in all_products if p.category.slug.endswith('-sensors')]
        boards = [p for p in all_products if p.category.slug.endswith('-boards')]

        # Ion — Order 1: delivered, sensors
        self._create_one_order(
            user=ion, status='delivered',
            items=[(sensors[0], 2), (sensors[1], 1), (sensors[3], 1)],
            shipping_name='Ion Popescu',
            shipping_address='Str. Mihai Eminescu nr. 15, Sector 1',
            shipping_city='București',
            shipping_zip='010123',
        )

        # Ion — Order 2: shipped, boards
        self._create_one_order(
            user=ion, status='shipped',
            items=[(boards[0], 1), (boards[1], 1)] if len(boards) >= 2 else [(boards[0], 2)],
            shipping_name='Ion Popescu',
            shipping_address='Str. Memorandumului nr. 28, Ap. 5',
            shipping_city='Cluj-Napoca',
            shipping_zip='400114',
        )

        # Ion — Order 3: pending, mixed
        mixed = [all_products[5], all_products[10], all_products[15], all_products[20]] if len(all_products) > 20 else all_products[:4]
        self._create_one_order(
            user=ion, status='pending',
            items=[(pr, 1) for pr in mixed],
            shipping_name='Ion Popescu',
            shipping_address='Str. Mihai Eminescu nr. 15, Sector 1',
            shipping_city='București',
            shipping_zip='010123',
        )

        # Maria — Order 1: confirmed
        self._create_one_order(
            user=maria, status='confirmed',
            items=[(all_products[2], 1), (all_products[8], 1)],
            shipping_name='Maria Ionescu',
            shipping_address='Bd. Revoluției nr. 5, Ap. 12',
            shipping_city='Timișoara',
            shipping_zip='300034',
        )

    def _create_one_order(self, user, status, items, shipping_name, shipping_address, shipping_city, shipping_zip):
        total = sum(p.price * qty for p, qty in items)
        order = Order.objects.create(
            user=user,
            status=status,
            total=total,
            shipping_name=shipping_name,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_zip=shipping_zip,
            shipping_country='Romania',
        )
        for product, qty in items:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                unit_price=product.price,
            )
        self.counts['orders'] += 1
        self.stdout.write(f'  [OK] Created order #{order.id} ({status}) for {user.username}')
