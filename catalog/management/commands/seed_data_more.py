from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
import random

from catalog.models import Category, AttributeDefinition, Product, ProductAttribute, Platform


class Command(BaseCommand):
    help = 'Seeds the database with additional automation products (extension to seed_data).'

    def handle(self, *args, **options):
        self.stdout.write('Seeding additional data...\n')
        self.counts = {'attributes': 0, 'products': 0}

        with transaction.atomic():
            platforms = {p.slug: p for p in Platform.objects.all()}
            self._create_more_attributes()
            self._create_more_products(platforms)

        c = self.counts
        self.stdout.write(self.style.SUCCESS(
            f"\nDone: {c['attributes']} new attribute definitions, "
            f"{c['products']} new products"
        ))

    def _make_product(self, cat_slug, data, plat_map):
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

        platform_objs = [plat_map[s] for s in platforms_list if s in plat_map]
        product.compatible_platforms.set(platform_objs)

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

    # ──────────────────────────────────────────────
    # NEW ATTRIBUTE DEFINITIONS (for empty categories)
    # ──────────────────────────────────────────────
    def _create_more_attributes(self):
        defs = {
            'solenoids': [
                ('Tensiune bobină', 'coil_voltage', 'float', 'V', True),
                ('Forță tracțiune', 'pull_force', 'float', 'N', True),
                ('Cursă', 'stroke_length', 'float', 'mm', True),
                ('Factor de utilizare', 'duty_cycle', 'string', '', True),
                ('Tip solenoid', 'solenoid_type', 'string', '', True),
                ('Grad protecție', 'ip_rating', 'string', '', False),
            ],
            'wifi-modules': [
                ('Standard WiFi', 'standard', 'string', '', True),
                ('Tip antenă', 'antenna', 'string', '', True),
                ('Interfață', 'interface', 'string', '', True),
                ('Putere transmisie', 'tx_power', 'float', 'dBm', True),
                ('Tensiune alimentare', 'supply_voltage', 'float', 'V', True),
                ('Rază de acțiune', 'range_meters', 'float', 'm', False),
            ],
            'bluetooth-modules': [
                ('Versiune Bluetooth', 'bt_version', 'string', '', True),
                ('Profil', 'profile', 'string', '', True),
                ('Interfață', 'interface', 'string', '', True),
                ('Rază de acțiune', 'range_meters', 'float', 'm', True),
                ('Tensiune alimentare', 'supply_voltage', 'float', 'V', True),
                ('Putere transmisie', 'tx_power', 'float', 'dBm', False),
            ],
            'lora-modules': [
                ('Frecvență', 'frequency', 'float', 'MHz', True),
                ('Putere transmisie', 'tx_power', 'float', 'dBm', True),
                ('Sensibilitate', 'sensitivity', 'float', 'dBm', True),
                ('Interfață', 'interface', 'string', '', True),
                ('Rază de acțiune', 'range_km', 'float', 'km', True),
                ('Tensiune alimentare', 'supply_voltage', 'float', 'V', True),
                ('Spreading factor', 'spreading_factor', 'string', '', False),
            ],
            'rs485-modules': [
                ('Interfață', 'interface', 'string', '', True),
                ('Rată baud', 'baud_rate', 'int', 'bps', True),
                ('Izolație galvanică', 'isolation', 'string', '', True),
                ('Număr noduri', 'node_count', 'int', '', True),
                ('Tensiune alimentare', 'supply_voltage', 'float', 'V', True),
                ('Protecție', 'protection', 'string', '', False),
            ],
            'raspberry-pi-boards': [
                ('CPU', 'cpu', 'string', '', True),
                ('RAM', 'ram', 'int', 'GB', True),
                ('Conectivitate', 'connectivity', 'string', '', True),
                ('Porturi USB', 'usb_ports', 'int', '', True),
                ('Pini GPIO', 'gpio_pins', 'int', '', True),
                ('Rezoluție maximă', 'max_resolution', 'string', '', False),
            ],
            'plc-modules': [
                ('CPU', 'cpu', 'string', '', True),
                ('Intrări digitale', 'digital_inputs', 'int', '', True),
                ('Ieșiri digitale', 'digital_outputs', 'int', '', True),
                ('Intrări analogice', 'analog_inputs', 'int', '', True),
                ('Comunicație', 'communication', 'string', '', True),
                ('Tensiune alimentare', 'supply_voltage', 'float', 'V', True),
                ('Limbaj programare', 'programming_language', 'string', '', False),
            ],
            'din-rail-psu': [
                ('Tensiune intrare', 'input_voltage', 'range', 'V', True),
                ('Tensiune ieșire', 'output_voltage', 'float', 'V', True),
                ('Curent ieșire', 'output_current', 'float', 'A', True),
                ('Putere ieșire', 'output_power', 'float', 'W', True),
                ('Eficiență', 'efficiency', 'float', '%', True),
                ('Protecție', 'protection', 'string', '', False),
            ],
            'dc-dc-converters': [
                ('Interval intrare', 'input_range', 'range', 'V', True),
                ('Tensiune ieșire', 'output_voltage', 'float', 'V', True),
                ('Curent maxim', 'max_current', 'float', 'A', True),
                ('Tip convertor', 'converter_type', 'string', '', True),
                ('Eficiență', 'efficiency', 'float', '%', True),
                ('Tensiune alimentare', 'supply_voltage', 'float', 'V', False),
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

        self.stdout.write(f'  [OK] Created {self.counts["attributes"]} new attribute definitions')

    # ──────────────────────────────────────────────
    # PRODUCTS
    # ──────────────────────────────────────────────
    def _create_more_products(self, plat):
        self._extend_pressure_sensors(plat)
        self._extend_proximity_sensors(plat)
        self._extend_motion_sensors(plat)
        self._extend_gas_sensors(plat)
        self._extend_humidity_sensors(plat)
        self._extend_distance_sensors(plat)
        self._extend_light_sensors(plat)
        self._extend_dc_motors(plat)
        self._extend_servo_motors(plat)
        self._extend_stepper_motors(plat)
        self._extend_relays(plat)
        self._extend_arduino_boards(plat)
        self._extend_esp_boards(plat)
        self._seed_solenoids(plat)
        self._seed_wifi_modules(plat)
        self._seed_bluetooth_modules(plat)
        self._seed_lora_modules(plat)
        self._seed_rs485_modules(plat)
        self._seed_raspberry_pi_boards(plat)
        self._seed_plc_modules(plat)
        self._seed_din_rail_psu(plat)
        self._seed_dc_dc_converters(plat)
        self.stdout.write(f'  [OK] Created {self.counts["products"]} additional products')

    # ---------- Extend Pressure Sensors (2 new) ----------
    def _extend_pressure_sensors(self, p):
        cat = 'pressure-sensors'
        products = [
            {
                'name': 'MPS20N0040D Senzor presiune diferentiala 40kPa',
                'slug': 'mps20n0040d-differential-40kpa',
                'sku': 'PRS-00100',
                'manufacturer': 'NXP',
                'price': 28.50,
                'stock': 60,
                'description': 'Senzor de presiune diferentiala cu sensibilitate ridicata, ideal pentru sfigmomanometre digitale si aplicatii de monitorizare a fluxului de aer. Ofera o iesire analogica liniara proportionala cu diferenta de presiune dintre cele doua porturi. Foarte popular in proiectele DIY de tensiometre si echipamente medicale.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32'],
                'attrs': {
                    'pressure_range': (0, 0.4),
                    'accuracy': 1.5,
                    'pressure_type': 'Diferentiala',
                    'output_signal': 'Analog mV',
                    'supply_voltage': 5.0,
                    'media_compatible': 'Aer, gaze neagresive',
                }
            },
            {
                'name': 'Honeywell ABP2 Senzor presiune absoluta I2C',
                'slug': 'honeywell-abp2-absolute-i2c',
                'sku': 'PRS-00101',
                'manufacturer': 'Honeywell',
                'price': 145.00,
                'stock': 25,
                'description': 'Senzor de presiune absoluta din seria ABP2 cu interfata digitala I2C si compensare integrata de temperatura. Ofera o precizie de plus-minus 0.25 procente FS pe intregul interval de operare si calibrare din fabrica. Construit pentru aplicatii industriale exigente si medicale care necesita stabilitate pe termen lung.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'pressure_range': (0, 1.6),
                    'accuracy': 0.25,
                    'pressure_type': 'Absoluta',
                    'output_signal': 'I2C',
                    'supply_voltage': 3.3,
                    'media_compatible': 'Aer, gaze neagresive',
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Extend Proximity Sensors (2 new) ----------
    def _extend_proximity_sensors(self, p):
        cat = 'proximity-sensors'
        products = [
            {
                'name': 'TCRT5000 Senzor reflexiv IR proximitate',
                'slug': 'tcrt5000-ir-reflective',
                'sku': 'PRX-00100',
                'manufacturer': 'Vishay',
                'price': 6.50,
                'stock': 200,
                'description': 'Senzor reflexiv cu LED IR si fototranzistor integrate, ideal pentru detectia obiectelor la distante foarte mici si aplicatii de urmarire linie pentru roboti. Ofera o distanta optima de detectie de 2.5mm si raspuns rapid. Foarte folosit in proiectele de line-following si encoder optic DIY.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp8266', 'esp32'],
                'attrs': {
                    'detect_distance': 2.5,
                    'sensor_type': 'Optic reflexiv',
                    'output_type': 'Analog',
                    'supply_voltage': (3.3, 5.0),
                    'switch_freq': 1000.0,
                    'ip_rating': 'IP20',
                }
            },
            {
                'name': 'Omron E2B-M18KS08 Senzor inductiv 8mm PNP',
                'slug': 'omron-e2b-m18ks08-inductive',
                'sku': 'PRX-00101',
                'manufacturer': 'Omron',
                'price': 95.00,
                'stock': 40,
                'description': 'Senzor inductiv industrial cu corp metalic M18 si distanta de detectie de 8mm pentru obiecte metalice. Constructie IP67 robusta pentru medii dure de productie si iesire PNP NO compatibila cu orice intrare digitala PLC. Garantat pentru milioane de cicluri de comutare.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'detect_distance': 8.0,
                    'sensor_type': 'Inductiv',
                    'output_type': 'PNP NO',
                    'supply_voltage': (10, 30),
                    'switch_freq': 500.0,
                    'ip_rating': 'IP67',
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Extend Motion Sensors (3 new) ----------
    def _extend_motion_sensors(self, p):
        cat = 'motion-sensors'
        products = [
            {
                'name': 'LIS3DH Accelerometru 3-axe ultra low-power',
                'slug': 'lis3dh-3axis-low-power',
                'sku': 'MOT-00100',
                'manufacturer': 'STMicroelectronics',
                'price': 19.50,
                'stock': 70,
                'description': 'Accelerometru digital cu 3 axe si consum ultra-redus, ideal pentru dispozitive portabile alimentate pe baterii. Ofera scale selectabile plus-minus 2/4/8/16g si interfata I2C/SPI. Include functii integrate de detectare a caderii libere si click pentru wake-up.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'detection_angle': 360.0,
                    'detect_distance': 0.0,
                    'sensor_type': 'Accelerometru',
                    'supply_voltage': (1.7, 3.6),
                    'delay_time': (0, 0),
                }
            },
            {
                'name': 'MPU9250 IMU 9-DOF girometru accelerometru magnetometru',
                'slug': 'mpu9250-9dof-imu',
                'sku': 'MOT-00101',
                'manufacturer': 'InvenSense',
                'price': 42.00,
                'stock': 55,
                'description': 'Modul IMU cu 9 grade de libertate care combina accelerometru, giroscop si magnetometru pe un singur chip. Perfect pentru aplicatii de orientare, drone, AHRS si navigatie inertiala. Procesor DMP integrat pentru fuziunea senzorilor direct pe modul.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'detection_angle': 360.0,
                    'detect_distance': 0.0,
                    'sensor_type': 'IMU 9-DOF',
                    'supply_voltage': (2.4, 3.6),
                    'delay_time': (0, 0),
                }
            },
            {
                'name': 'Panasonic EKMC PaPIRs senzor PIR digital',
                'slug': 'panasonic-ekmc-papirs-pir',
                'sku': 'MOT-00102',
                'manufacturer': 'Panasonic',
                'price': 78.00,
                'stock': 35,
                'description': 'Senzor PIR profesional cu iesire digitala directa si lentila Fresnel cu unghi larg de 96 grade. Detecteaza miscarea la distante de pana la 12 metri cu un consum extrem de redus. Ideal pentru sisteme de iluminare automata, alarme si smart home de calitate.',
                'platforms': ['arduino-uno', 'esp8266', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'detection_angle': 96.0,
                    'detect_distance': 12.0,
                    'sensor_type': 'PIR',
                    'supply_voltage': (3.0, 6.0),
                    'delay_time': (2, 2),
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Extend Gas Sensors (2 new) ----------
    def _extend_gas_sensors(self, p):
        cat = 'gas-sensors'
        products = [
            {
                'name': 'MQ4 Senzor metan gaz natural',
                'slug': 'mq4-methane-natural-gas',
                'sku': 'GAS-00100',
                'manufacturer': 'Hanwei',
                'price': 16.50,
                'stock': 80,
                'description': 'Senzor semiconductor sensibil la metan si gaz natural, cu iesire analogica si digitala cu prag reglabil. Folosit frecvent in detectoare de scurgeri de gaz pentru bucatarii si instalatii de incalzire. Necesita o perioada de preincalzire pentru stabilizare optima.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp8266', 'esp32'],
                'attrs': {
                    'gas_type': 'CH4 (Metan)',
                    'ppm_range': (200, 10000),
                    'warmup_time': 24.0,
                    'supply_voltage': 5.0,
                    'output_type': 'Analog + Digital',
                }
            },
            {
                'name': 'SCD30 Senzor CO2 NDIR cu temperatura si umiditate',
                'slug': 'scd30-ndir-co2-temp-rh',
                'sku': 'GAS-00101',
                'manufacturer': 'Sensirion',
                'price': 245.00,
                'stock': 20,
                'description': 'Senzor de CO2 cu tehnologie NDIR pentru masurari precise si stabile pe termen lung, fara drift specific senzorilor MOX. Include si masurarea temperaturii si umiditatii intr-un singur modul I2C compact. Ideal pentru monitorizarea calitatii aerului in interior si HVAC inteligent.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'gas_type': 'CO2',
                    'ppm_range': (400, 10000),
                    'warmup_time': 2.0,
                    'supply_voltage': 3.3,
                    'output_type': 'I2C',
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Extend Humidity Sensors (4 new) ----------
    def _extend_humidity_sensors(self, p):
        cat = 'humidity-sensors'
        products = [
            {
                'name': 'HDC1080 Senzor umiditate I2C precizie ridicata',
                'slug': 'hdc1080-i2c-precision-humidity',
                'sku': 'HUM-00100',
                'manufacturer': 'Texas Instruments',
                'price': 24.00,
                'stock': 65,
                'description': 'Senzor de umiditate si temperatura cu interfata I2C si consum extrem de redus. Ofera o precizie de plus-minus 2 procente RH si stabilitate excelenta pe termen lung. Ideal pentru aplicatii industriale, HVAC si dispozitive IoT alimentate pe baterii.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'humidity_range': (0, 100),
                    'humidity_acc': 2.0,
                    'temp_range': (-40, 125),
                    'interface': 'I2C',
                    'sensor_type': 'Capacitiv',
                }
            },
            {
                'name': 'SHT21 Senzor umiditate Sensirion I2C',
                'slug': 'sht21-sensirion-humidity-i2c',
                'sku': 'HUM-00101',
                'manufacturer': 'Sensirion',
                'price': 38.50,
                'stock': 45,
                'description': 'Senzor digital de umiditate si temperatura din celebra serie SHT2x cu calibrare din fabrica. Ofera repetabilitate excelenta si raspuns rapid intr-un format SMD compact. Folosit larg in echipamente medicale, automotive si industriale.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'humidity_range': (0, 100),
                    'humidity_acc': 3.0,
                    'temp_range': (-40, 125),
                    'interface': 'I2C',
                    'sensor_type': 'Capacitiv',
                }
            },
            {
                'name': 'AHT20 Senzor umiditate calibrat I2C',
                'slug': 'aht20-calibrated-humidity',
                'sku': 'HUM-00102',
                'manufacturer': 'Aosong',
                'price': 11.90,
                'stock': 110,
                'description': 'Senzor digital de noua generatie pentru umiditate si temperatura, succesor al popularului DHT22. Ofera precizie imbunatatita, comunicare I2C standard si un timp de raspuns mult mai rapid. Optiune economica pentru proiecte de monitorizare a mediului.',
                'platforms': ['arduino-uno', 'esp8266', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'humidity_range': (0, 100),
                    'humidity_acc': 2.0,
                    'temp_range': (-40, 85),
                    'interface': 'I2C',
                    'sensor_type': 'Capacitiv',
                }
            },
            {
                'name': 'Rotronic HC2A-S Sonda industriala umiditate',
                'slug': 'rotronic-hc2a-s-industrial-probe',
                'sku': 'HUM-00103',
                'manufacturer': 'Rotronic',
                'price': 890.00,
                'stock': 8,
                'description': 'Sonda industriala profesionala pentru umiditate si temperatura cu iesire analogica 4-20mA si tija metalica de 200mm. Construita pentru aplicatii exigente in industria farmaceutica, alimentara si depozite climatizate. Calibrare trasabila la standard NIST inclusa.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'humidity_range': (0, 100),
                    'humidity_acc': 0.8,
                    'temp_range': (-50, 200),
                    'interface': '4-20mA',
                    'sensor_type': 'Capacitiv',
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Extend Distance Sensors (3 new) ----------
    def _extend_distance_sensors(self, p):
        cat = 'distance-sensors'
        products = [
            {
                'name': 'VL53L1X Senzor ToF laser 4m I2C',
                'slug': 'vl53l1x-tof-4m-laser',
                'sku': 'DST-00100',
                'manufacturer': 'STMicroelectronics',
                'price': 48.00,
                'stock': 60,
                'description': 'Senzor de distanta laser ToF (Time of Flight) cu raza extinsa de pana la 4 metri, ideal pentru aplicatii de robotica si masurari precise. Include capabilitate de configurare a zonei de interes si rate de masurare pana la 50Hz. Comunica prin I2C cu majoritatea microcontrolerelor moderne.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'measure_range': (4, 400),
                    'accuracy': 5.0,
                    'technology': 'Laser ToF',
                    'beam_angle': 27.0,
                    'supply_voltage': 3.3,
                    'interface': 'I2C',
                }
            },
            {
                'name': 'US-100 Senzor ultrasonic cu compensare temperatura',
                'slug': 'us-100-ultrasonic-temp-comp',
                'sku': 'DST-00101',
                'manufacturer': 'AdaFruit',
                'price': 22.50,
                'stock': 90,
                'description': 'Senzor ultrasonic mai precis decat HC-SR04 datorita compensarii integrate de temperatura. Suporta doua moduri de operare: trigger/echo si UART. Acuratete imbunatatita pentru proiectele care necesita masurari fiabile in conditii variabile de mediu.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp8266', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'measure_range': (2, 450),
                    'accuracy': 3.0,
                    'technology': 'Ultrasonic',
                    'beam_angle': 15.0,
                    'supply_voltage': 5.0,
                    'interface': 'GPIO / UART',
                }
            },
            {
                'name': 'RPLIDAR A1M8 Scanner laser 360 grade',
                'slug': 'rplidar-a1m8-360-scanner',
                'sku': 'DST-00102',
                'manufacturer': 'Slamtec',
                'price': 525.00,
                'stock': 12,
                'description': 'Scanner LiDAR 2D cu raza de 12 metri si rotatie completa 360 grade pentru aplicatii SLAM si robotica mobila. Genereaza pana la 8000 puncte/secunda si suporta integrare cu ROS. Folosit pe scara larga in robotii cu mapare si navigatie autonoma.',
                'platforms': ['raspberry-pi', 'stm32'],
                'attrs': {
                    'measure_range': (15, 1200),
                    'accuracy': 10.0,
                    'technology': 'LiDAR 2D',
                    'beam_angle': 360.0,
                    'supply_voltage': 5.0,
                    'interface': 'UART USB',
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Extend Light Sensors (4 new) ----------
    def _extend_light_sensors(self, p):
        cat = 'light-sensors'
        products = [
            {
                'name': 'TSL2561 Senzor lumina digital I2C',
                'slug': 'tsl2561-digital-light-i2c',
                'sku': 'LGT-00100',
                'manufacturer': 'AMS',
                'price': 17.50,
                'stock': 85,
                'description': 'Senzor digital de lumina ambianta cu doi fotodiode (vizibil + IR) pentru o aproximare precisa a raspunsului ochiului uman. Comunica prin I2C si ofera un interval dinamic de 0.1 la 40000 lux. Foarte folosit in dispozitive cu reglare automata a luminozitatii ecranului.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'lux_range': (0.1, 40000),
                    'spectrum': 'Vizibil + IR',
                    'interface': 'I2C',
                    'supply_voltage': 3.3,
                }
            },
            {
                'name': 'APDS-9960 Senzor gesturi proximitate culoare',
                'slug': 'apds-9960-gesture-color',
                'sku': 'LGT-00101',
                'manufacturer': 'Avago',
                'price': 32.00,
                'stock': 55,
                'description': 'Modul multi-functional care combina senzori pentru lumina ambianta, proximitate, culoare RGB si recunoastere gesturi. Perfect pentru interfete touchless si dispozitive smart home. Comunica prin I2C cu intrerupere configurabila.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'lux_range': (0, 65535),
                    'spectrum': 'RGB + IR',
                    'interface': 'I2C',
                    'supply_voltage': 3.3,
                }
            },
            {
                'name': 'TEMT6000 Senzor lumina analog',
                'slug': 'temt6000-analog-light',
                'sku': 'LGT-00102',
                'manufacturer': 'Vishay',
                'price': 9.50,
                'stock': 130,
                'description': 'Senzor analog simplu de lumina ambianta cu raspuns spectral apropiat de cel al ochiului uman. Iesire analogica liniara conectabila direct la un pin ADC. Optiune ieftina si fiabila pentru proiecte simple de iluminat automat.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp8266', 'esp32'],
                'attrs': {
                    'lux_range': (1, 1000),
                    'spectrum': 'Vizibil',
                    'interface': 'Analog',
                    'supply_voltage': 5.0,
                }
            },
            {
                'name': 'GUVA-S12SD Senzor UV analog',
                'slug': 'guva-s12sd-uv-analog',
                'sku': 'LGT-00103',
                'manufacturer': 'GenUV',
                'price': 26.00,
                'stock': 50,
                'description': 'Senzor analog pentru radiatia ultravioleta in spectrul 240-370nm cu iesire liniara in mV proportionala cu indexul UV. Ideal pentru statii meteo, dozimetre UV portabile si dispozitive de monitorizare a expunerii la soare. Folosit frecvent in proiecte de outdoor IoT.',
                'platforms': ['arduino-uno', 'esp8266', 'esp32'],
                'attrs': {
                    'lux_range': (0, 1000),
                    'spectrum': 'UV (240-370nm)',
                    'interface': 'Analog',
                    'supply_voltage': 5.0,
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Extend DC Motors (5 new) ----------
    def _extend_dc_motors(self, p):
        cat = 'dc-motors'
        products = [
            {
                'name': 'Motor DC N20 6V 200RPM cu reductor',
                'slug': 'n20-dc-motor-6v-200rpm',
                'sku': 'DCM-00100',
                'manufacturer': 'Pololu',
                'price': 32.00,
                'stock': 75,
                'description': 'Micromotor DC cu reductor de tip N20, popular in proiectele de robotica miniatura si BEAM. Dimensiunile compacte si raportul redus de transmisie ofera un cuplu rezonabil la dimensiuni de doar 12mm diametru. Folosit in robotii mici autonomi si sumo.',
                'platforms': ['arduino-uno', 'esp32'],
                'attrs': {
                    'voltage': 6.0,
                    'current': 0.2,
                    'rpm': 200.0,
                    'power': 1.2,
                    'motor_type': 'DC cu reductor',
                }
            },
            {
                'name': 'Motor DC 24V 100W cu encoder magnetic',
                'slug': 'dc-motor-24v-100w-encoder',
                'sku': 'DCM-00101',
                'manufacturer': 'Maxon',
                'price': 485.00,
                'stock': 15,
                'description': 'Motor industrial DC de 100W cu encoder magnetic integrat pentru control precis al pozitiei si vitezei. Constructie din aluminiu cu rulmenti de calitate pentru o durata lunga de viata. Folosit in roboti mobili industriali si AGV-uri.',
                'platforms': ['arduino-mega', 'stm32', 'plc-siemens-s7'],
                'attrs': {
                    'voltage': 24.0,
                    'current': 5.0,
                    'rpm': 3000.0,
                    'power': 100.0,
                    'motor_type': 'DC cu encoder',
                }
            },
            {
                'name': 'Motor DC 12V 2A pompa peristaltica',
                'slug': 'dc-motor-12v-peristaltic-pump',
                'sku': 'DCM-00102',
                'manufacturer': 'Kamoer',
                'price': 145.00,
                'stock': 25,
                'description': 'Pompa peristaltica cu motor DC integrat pentru dozare precisa de lichide la debit reglabil. Ideala pentru acvaristica automatizata, sisteme hidroponice si chimie de laborator. Nu permite contactul lichidului cu mecanismul pompei.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'voltage': 12.0,
                    'current': 0.5,
                    'rpm': 100.0,
                    'power': 6.0,
                    'motor_type': 'Pompa peristaltica',
                }
            },
            {
                'name': 'Motor DC 3-6V mini cu propeller pentru drone',
                'slug': 'dc-mini-motor-3-6v-propeller',
                'sku': 'DCM-00103',
                'manufacturer': 'DYS',
                'price': 14.50,
                'stock': 200,
                'description': 'Motor coreless miniatural pentru micro-drone si elicoptere RC cu turatie foarte ridicata. Constructie usoara cu duza din metal si rulmenti precisi. Compatibil cu propellere standard de 55mm.',
                'platforms': ['arduino-uno', 'esp8266', 'esp32'],
                'attrs': {
                    'voltage': 5.0,
                    'current': 0.3,
                    'rpm': 50000.0,
                    'power': 1.5,
                    'motor_type': 'Coreless brushless',
                }
            },
            {
                'name': 'Motor DC JGY-370 worm gear 12V autoblocant',
                'slug': 'jgy-370-worm-gear-12v',
                'sku': 'DCM-00104',
                'manufacturer': 'JGY',
                'price': 68.00,
                'stock': 40,
                'description': 'Motor DC cu reductor melcat (worm gear) autoblocant, ideal pentru aplicatii unde nu se doreste rotatia inversa sub sarcina. Cuplul ridicat la turatie redusa il face perfect pentru deschideri automate de usi si bariere. Functioneaza la 12V cu un consum moderat.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32'],
                'attrs': {
                    'voltage': 12.0,
                    'current': 0.6,
                    'rpm': 30.0,
                    'power': 7.2,
                    'motor_type': 'DC worm gear',
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Extend Servo Motors (3 new) ----------
    def _extend_servo_motors(self, p):
        cat = 'servo-motors'
        products = [
            {
                'name': 'Hitec HS-422 Servo analog standard',
                'slug': 'hitec-hs-422-analog-standard',
                'sku': 'SRV-00100',
                'manufacturer': 'Hitec',
                'price': 89.00,
                'stock': 35,
                'description': 'Servo analog standard de calitate, foarte fiabil si folosit in modele RC si proiecte de robotica medie. Ofera un raport excelent calitate-pret cu rulmenti din nylon si motor coreless. Compatibil cu majoritatea sistemelor de receptie RC.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32'],
                'attrs': {
                    'supply_voltage': (4.8, 6.0),
                    'torque': 3.3,
                    'rotation_angle': 180.0,
                    'servo_type': 'Analog standard',
                }
            },
            {
                'name': 'Savox SC-1258TG Servo digital coreless titanium',
                'slug': 'savox-sc-1258tg-digital',
                'sku': 'SRV-00101',
                'manufacturer': 'Savox',
                'price': 395.00,
                'stock': 12,
                'description': 'Servo digital de inalta performanta cu reductor din titaniu si motor coreless pentru viteza si precizie maxime. Foarte folosit in concursurile de drift RC si aplicatii high-end de robotica. Tensiune ridicata pentru cuplu si raspuns optime.',
                'platforms': ['arduino-uno', 'stm32'],
                'attrs': {
                    'supply_voltage': (6.0, 7.4),
                    'torque': 12.0,
                    'rotation_angle': 180.0,
                    'servo_type': 'Digital coreless',
                }
            },
            {
                'name': 'Dynamixel AX-12A Servo inteligent serial',
                'slug': 'dynamixel-ax-12a-smart-servo',
                'sku': 'SRV-00102',
                'manufacturer': 'Robotis',
                'price': 295.00,
                'stock': 18,
                'description': 'Servo robotic inteligent cu comunicare seriala TTL, feedback de pozitie, temperatura, tensiune si curent in timp real. Folosit in robotii umanoizi educationali si bratele manipulatoare. Permite daisy-chain pentru zeci de servo-uri pe o singura magistrala.',
                'platforms': ['arduino-mega', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'supply_voltage': (9.0, 12.0),
                    'torque': 15.3,
                    'rotation_angle': 300.0,
                    'servo_type': 'Smart serial bus',
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Extend Stepper Motors (5 new) ----------
    def _extend_stepper_motors(self, p):
        cat = 'stepper-motors'
        products = [
            {
                'name': 'NEMA17 17HS4401 Stepper 40N.cm bipolar',
                'slug': 'nema17-17hs4401-40ncm',
                'sku': 'STP-00100',
                'manufacturer': 'Wantai',
                'price': 75.00,
                'stock': 60,
                'description': 'Motor pas cu pas NEMA17 standard pentru imprimante 3D, masini CNC mici si plotere. Cuplul de retentie de 40N.cm si curentul moderat il fac compatibil cu majoritatea driverelor populare ca A4988 sau DRV8825. Cabluri de 1m incluse.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32', 'stm32'],
                'attrs': {
                    'step_angle': 1.8,
                    'current_phase': 1.7,
                    'holding_torque': 0.4,
                    'wire_count': 4,
                }
            },
            {
                'name': 'NEMA17 cu shaft lung pentru axa Z imprimanta 3D',
                'slug': 'nema17-long-shaft-z-axis',
                'sku': 'STP-00101',
                'manufacturer': 'Moons',
                'price': 95.00,
                'stock': 40,
                'description': 'Motor stepper NEMA17 cu shaft lung de 22mm filetat pentru axa Z a imprimantelor 3D. Permite cuplarea directa cu surub trapezoidal sau filetat T8. Constructie premium cu rulmenti de calitate pentru zgomot redus.',
                'platforms': ['arduino-mega', 'stm32'],
                'attrs': {
                    'step_angle': 1.8,
                    'current_phase': 1.5,
                    'holding_torque': 0.45,
                    'wire_count': 4,
                }
            },
            {
                'name': 'NEMA34 86HS156 Stepper industrial 12N.m',
                'slug': 'nema34-86hs156-industrial',
                'sku': 'STP-00102',
                'manufacturer': 'Leadshine',
                'price': 425.00,
                'stock': 10,
                'description': 'Motor stepper industrial de mare cuplu pentru CNC-uri de gabarit mediu si mare, freze si masini de gravat. Necesita driver industrial dedicat de 4-8A si o sursa de minim 48V. Constructie robusta cu fixare standard NEMA34.',
                'platforms': ['stm32', 'plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'step_angle': 1.8,
                    'current_phase': 6.0,
                    'holding_torque': 12.0,
                    'wire_count': 4,
                }
            },
            {
                'name': 'NEMA14 stepper compact 14N.cm',
                'slug': 'nema14-compact-14ncm',
                'sku': 'STP-00103',
                'manufacturer': 'StepperOnline',
                'price': 58.00,
                'stock': 35,
                'description': 'Motor stepper de gabarit redus din seria NEMA14 ideal pentru extrudere imprimante 3D si proiecte unde spatiul si greutatea sunt critice. Ofera o rezolutie excelenta cu microstepping. Compatibil cu drivere standard A4988.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32', 'stm32'],
                'attrs': {
                    'step_angle': 1.8,
                    'current_phase': 1.0,
                    'holding_torque': 0.14,
                    'wire_count': 4,
                }
            },
            {
                'name': 'NEMA17 inalt cuplu 65N.cm pancake redus',
                'slug': 'nema17-pancake-high-torque',
                'sku': 'STP-00104',
                'manufacturer': 'OMC',
                'price': 145.00,
                'stock': 22,
                'description': 'Motor stepper NEMA17 de inaltime mai mare pentru cuplu maxim, ideal pentru axa Y a imprimantelor 3D mari sau aplicatii de extrudere directe. Cuplu de retentie de 65N.cm depaseste cu mult versiunile standard. Constructie cu izolatie termica imbunatatita.',
                'platforms': ['arduino-mega', 'stm32'],
                'attrs': {
                    'step_angle': 1.8,
                    'current_phase': 2.0,
                    'holding_torque': 0.65,
                    'wire_count': 4,
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Extend Relays (4 new) ----------
    def _extend_relays(self, p):
        cat = 'relays'
        products = [
            {
                'name': 'Modul releu 5V 2 canale cu optocuplor',
                'slug': 'relay-module-5v-2ch-opto',
                'sku': 'RLY-00100',
                'manufacturer': 'SongLe',
                'price': 15.50,
                'stock': 130,
                'description': 'Modul cu 2 relee electromagnetice de 10A si optocuploare pentru izolarea galvanica de microcontroler. Activate prin nivel LOW pe pinii de control si compatibile direct cu Arduino, ESP si Raspberry Pi. Indicatori LED pentru fiecare canal activ.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp8266', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'coil_voltage': 5.0,
                    'max_current': 10.0,
                    'max_voltage_ac': 250.0,
                    'relay_type': 'Electromagnetic SPDT',
                }
            },
            {
                'name': 'Modul releu 5V 16 canale industrial',
                'slug': 'relay-module-5v-16ch',
                'sku': 'RLY-00101',
                'manufacturer': 'SainSmart',
                'price': 145.00,
                'stock': 25,
                'description': 'Placa cu 16 relee de 10A pentru automatizari complexe si domotica. Toate canalele au optocuploare si LED-uri de stare individuale. Necesita o sursa separata pentru bobine la curent total ridicat. Ideal pentru proiectele de smart home cu multi consumatori.',
                'platforms': ['arduino-mega', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'coil_voltage': 5.0,
                    'max_current': 10.0,
                    'max_voltage_ac': 250.0,
                    'relay_type': 'Electromagnetic SPDT',
                }
            },
            {
                'name': 'Releu Finder 40.52 24VDC montaj soclu',
                'slug': 'finder-40-52-24vdc',
                'sku': 'RLY-00102',
                'manufacturer': 'Finder',
                'price': 38.50,
                'stock': 50,
                'description': 'Releu industrial de calitate cu doua contacte comutatoare (DPDT) si soclu de montaj pe sina DIN. Foarte folosit in panourile electrice pentru comanda iluminatului si echipamentelor. Garantat pentru milioane de cicluri si certificat conform IEC.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'coil_voltage': 24.0,
                    'max_current': 8.0,
                    'max_voltage_ac': 250.0,
                    'relay_type': 'Electromagnetic DPDT',
                }
            },
            {
                'name': 'SSR Fotek 40DA solid state 40A',
                'slug': 'fotek-ssr-40da-solid-state',
                'sku': 'RLY-00103',
                'manufacturer': 'Fotek',
                'price': 55.00,
                'stock': 40,
                'description': 'Releu solid-state de 40A cu intrare DC 3-32V si iesire AC 24-380V, ideal pentru controlul incalzitoarelor electrice si motoarelor mici. Comutare in zero crossing pentru zgomot electromagnetic minim. Necesita radiator pentru sarcini peste 10A.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi', 'plc-siemens-s7'],
                'attrs': {
                    'coil_voltage': 12.0,
                    'max_current': 40.0,
                    'max_voltage_ac': 380.0,
                    'relay_type': 'Solid State',
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Extend Arduino Boards (3 new) ----------
    def _extend_arduino_boards(self, p):
        cat = 'arduino-boards'
        products = [
            {
                'name': 'Arduino Leonardo R3 cu ATmega32u4',
                'slug': 'arduino-leonardo-r3',
                'sku': 'ARD-00100',
                'manufacturer': 'Arduino',
                'price': 125.00,
                'stock': 35,
                'description': 'Placa Arduino cu microcontroler ATmega32u4 care include suport nativ pentru USB HID, permitand emularea tastaturii si mouse-ului. Compatibila cu majoritatea shield-urilor Arduino Uno. Ideala pentru proiecte de input devices si automatizari de PC.',
                'platforms': ['arduino-uno'],
                'attrs': {
                    'mcu': 'ATmega32u4',
                    'operating_voltage': 5.0,
                    'digital_pins': 20,
                    'analog_pins': 12,
                    'flash_memory': 32,
                    'clock_freq': 16.0,
                    'connectivity': 'USB nativ',
                }
            },
            {
                'name': 'Arduino Due cu SAM3X8E ARM Cortex-M3',
                'slug': 'arduino-due-sam3x8e',
                'sku': 'ARD-00101',
                'manufacturer': 'Arduino',
                'price': 245.00,
                'stock': 20,
                'description': 'Placa Arduino de mare performanta cu procesor ARM Cortex-M3 pe 32 de biti la 84MHz. Ofera 54 pini digitali, 12 analogici si mai multe interfete UART, SPI si I2C. Perfect pentru proiecte complexe care depasesc limitele AVR.',
                'platforms': ['arduino-uno', 'arduino-mega'],
                'attrs': {
                    'mcu': 'AT91SAM3X8E',
                    'operating_voltage': 3.3,
                    'digital_pins': 54,
                    'analog_pins': 12,
                    'flash_memory': 512,
                    'clock_freq': 84.0,
                    'connectivity': 'USB',
                }
            },
            {
                'name': 'Arduino Pro Mini 5V 16MHz compact',
                'slug': 'arduino-pro-mini-5v-16mhz',
                'sku': 'ARD-00102',
                'manufacturer': 'SparkFun',
                'price': 32.00,
                'stock': 90,
                'description': 'Versiune miniaturizata a Arduino Uno fara conectorul USB si headerele pre-lipite. Ideala pentru integrare in proiecte finale si purtabile. Necesita un convertor FTDI extern pentru programare prin USB.',
                'platforms': ['arduino-uno'],
                'attrs': {
                    'mcu': 'ATmega328P',
                    'operating_voltage': 5.0,
                    'digital_pins': 14,
                    'analog_pins': 8,
                    'flash_memory': 32,
                    'clock_freq': 16.0,
                    'connectivity': 'Serial TTL',
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Extend ESP Boards (3 new) ----------
    def _extend_esp_boards(self, p):
        cat = 'esp-boards'
        products = [
            {
                'name': 'ESP32-C3 SuperMini placa RISC-V WiFi BLE',
                'slug': 'esp32-c3-supermini-riscv',
                'sku': 'ESP-00100',
                'manufacturer': 'Espressif',
                'price': 28.50,
                'stock': 110,
                'description': 'Placa ultra-compacta cu ESP32-C3 bazat pe arhitectura RISC-V cu WiFi si Bluetooth LE 5.0 integrate. Format mini cu USB-C ideal pentru proiecte purtabile si IoT. Performante excelente la pret redus.',
                'platforms': ['esp32'],
                'attrs': {
                    'main_chip': 'ESP32-C3',
                    'flash_memory': 4,
                    'ram': 400,
                    'connectivity': 'WiFi 2.4GHz, BLE 5.0',
                    'gpio_pins': 11,
                    'supply_voltage': 3.3,
                }
            },
            {
                'name': 'ESP32-S2 Mini Lolin cu USB OTG',
                'slug': 'esp32-s2-mini-lolin',
                'sku': 'ESP-00101',
                'manufacturer': 'WeMos',
                'price': 36.00,
                'stock': 70,
                'description': 'Placa ESP32-S2 cu single core Xtensa LX7 si suport USB OTG nativ. Lipseste Bluetooth dar are pini suplimentari GPIO si touch capacitiv. Format compatibil cu D1 Mini pentru schimbare facila in proiecte existente.',
                'platforms': ['esp32'],
                'attrs': {
                    'main_chip': 'ESP32-S2',
                    'flash_memory': 4,
                    'ram': 320,
                    'connectivity': 'WiFi 2.4GHz, USB OTG',
                    'gpio_pins': 27,
                    'supply_voltage': 3.3,
                }
            },
            {
                'name': 'ESP8266 ESP-01S modul WiFi minimal',
                'slug': 'esp8266-esp-01s-minimal',
                'sku': 'ESP-00102',
                'manufacturer': 'AI-Thinker',
                'price': 18.00,
                'stock': 150,
                'description': 'Cel mai compact modul ESP8266 cu doar 2 pini GPIO disponibili, ideal pentru proiecte simple WiFi-enabled. Memorie flash de 1MB suficienta pentru firmware-ul basic AT sau aplicatii MicroPython minime. Necesita convertor USB-Serial pentru programare.',
                'platforms': ['esp8266', 'arduino-uno', 'arduino-mega'],
                'attrs': {
                    'main_chip': 'ESP8266EX',
                    'flash_memory': 1,
                    'ram': 80,
                    'connectivity': 'WiFi 2.4GHz',
                    'gpio_pins': 2,
                    'supply_voltage': 3.3,
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Seed Solenoids (8 new) ----------
    def _seed_solenoids(self, p):
        cat = 'solenoids'
        products = [
            {
                'name': 'Solenoid push 12V 10N cursa 10mm',
                'slug': 'solenoid-push-12v-10n-10mm',
                'sku': 'SOL-00001',
                'manufacturer': 'Adafruit',
                'price': 65.00,
                'stock': 45,
                'description': 'Solenoid liniar de tip push pentru aplicatii de actionare scurta in proiecte de robotica si automatizari. Forta de tractiune de 10N la 12V cu duty cycle intermitent. Ideal pentru mecanisme de blocare, baterie de pian DIY si automatizari simple.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32'],
                'attrs': {
                    'coil_voltage': 12.0,
                    'pull_force': 10.0,
                    'stroke_length': 10.0,
                    'duty_cycle': '30 procente intermitent',
                    'solenoid_type': 'Push',
                    'ip_rating': 'IP20',
                }
            },
            {
                'name': 'Electrovalva 12V apa 1/2 inch normal inchisa',
                'slug': 'electrovalve-12v-water-half-inch',
                'sku': 'SOL-00002',
                'manufacturer': 'Burkert',
                'price': 89.00,
                'stock': 60,
                'description': 'Electrovalva tip solenoid pentru controlul fluxului de apa cu filet de 1/2 inch. Functioneaza la 12V DC si este normal inchisa, deschizandu-se la alimentarea bobinei. Foarte folosita in sisteme de irigatii automate si distributoare de apa.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp8266', 'esp32'],
                'attrs': {
                    'coil_voltage': 12.0,
                    'pull_force': 25.0,
                    'stroke_length': 5.0,
                    'duty_cycle': 'Continuu',
                    'solenoid_type': 'Push',
                    'ip_rating': 'IP65',
                }
            },
            {
                'name': 'Solenoid latching bistabil 6V 5N',
                'slug': 'solenoid-latching-6v-5n',
                'sku': 'SOL-00003',
                'manufacturer': 'Takaha',
                'price': 78.00,
                'stock': 30,
                'description': 'Solenoid bistabil cu memorie magnetica care isi pastreaza pozitia fara alimentare continua. Consumul redus de energie il face ideal pentru aplicatii alimentate pe baterii. Schimbare de pozitie cu impuls scurt in polaritati opuse.',
                'platforms': ['arduino-uno', 'esp32'],
                'attrs': {
                    'coil_voltage': 6.0,
                    'pull_force': 5.0,
                    'stroke_length': 6.0,
                    'duty_cycle': 'Impuls',
                    'solenoid_type': 'Latching',
                    'ip_rating': 'IP20',
                }
            },
            {
                'name': 'Solenoid pull industrial 24V 50N',
                'slug': 'solenoid-pull-24v-50n-industrial',
                'sku': 'SOL-00004',
                'manufacturer': 'Magnetic Sensor Systems',
                'price': 245.00,
                'stock': 18,
                'description': 'Solenoid industrial puternic de tip pull cu forta de 50N la 24V. Constructie robusta din otel cu finisaj anti-corodare pentru medii industriale dure. Folosit in automatizari industriale, sisteme de blocare si masini de turnare prin injectie.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'coil_voltage': 24.0,
                    'pull_force': 50.0,
                    'stroke_length': 15.0,
                    'duty_cycle': '100 procente continuu',
                    'solenoid_type': 'Pull',
                    'ip_rating': 'IP54',
                }
            },
            {
                'name': 'Electrovalva pneumatica 5/2 24VDC',
                'slug': 'pneumatic-valve-5-2-24vdc',
                'sku': 'SOL-00005',
                'manufacturer': 'SMC',
                'price': 185.00,
                'stock': 28,
                'description': 'Electrovalva pneumatica cu 5 cai si 2 pozitii pentru actionarea cilindrilor cu dublu efect. Comutare rapida cu bobina de 24V DC si presiune de operare pana la 10 bar. Folosita pe scara larga in automatizari pneumatice industriale.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'coil_voltage': 24.0,
                    'pull_force': 0.0,
                    'stroke_length': 0.0,
                    'duty_cycle': '100 procente continuu',
                    'solenoid_type': 'Push',
                    'ip_rating': 'IP65',
                }
            },
            {
                'name': 'Solenoid mini 5V 1.5N pentru micro proiecte',
                'slug': 'solenoid-mini-5v-1-5n',
                'sku': 'SOL-00006',
                'manufacturer': 'Sparkfun',
                'price': 35.00,
                'stock': 65,
                'description': 'Micro-solenoid alimentat la doar 5V cu forta de tractiune redusa, ideal pentru proiecte miniaturale si modele RC. Activarea directa de la un pin GPIO printr-un tranzistor MOSFET. Folosit in mecanisme delicate si dispozitive purtabile.',
                'platforms': ['arduino-uno', 'esp8266', 'esp32'],
                'attrs': {
                    'coil_voltage': 5.0,
                    'pull_force': 1.5,
                    'stroke_length': 4.0,
                    'duty_cycle': '30 procente intermitent',
                    'solenoid_type': 'Push',
                    'ip_rating': 'IP20',
                }
            },
            {
                'name': 'Electrovalva gaz natural 230VAC 3/4 inch',
                'slug': 'gas-valve-230vac-three-quarter',
                'sku': 'SOL-00007',
                'manufacturer': 'Madas',
                'price': 320.00,
                'stock': 15,
                'description': 'Electrovalva certificata pentru gaz natural si GPL cu filet 3/4 inch si alimentare 230VAC. Normal inchisa, se deschide doar cand sistemul de siguranta da semnal verde. Conforma standardelor europene EN161 pentru centrale termice.',
                'platforms': ['plc-siemens-s7'],
                'attrs': {
                    'coil_voltage': 230.0,
                    'pull_force': 0.0,
                    'stroke_length': 8.0,
                    'duty_cycle': 'Continuu',
                    'solenoid_type': 'Push',
                    'ip_rating': 'IP54',
                }
            },
            {
                'name': 'Solenoid rotativ 12V cu unghi 25 grade',
                'slug': 'rotary-solenoid-12v-25deg',
                'sku': 'SOL-00008',
                'manufacturer': 'Ledex',
                'price': 195.00,
                'stock': 12,
                'description': 'Solenoid de tip rotativ cu unghi fix de 25 grade, ideal pentru aplicatii de comutare mecanica rapida. Constructie din alama si otel pentru durabilitate ridicata. Folosit in sisteme de sortare, distributoare si echipamente de laborator.',
                'platforms': ['arduino-mega', 'stm32', 'plc-siemens-s7'],
                'attrs': {
                    'coil_voltage': 12.0,
                    'pull_force': 8.0,
                    'stroke_length': 0.0,
                    'duty_cycle': '50 procente intermitent',
                    'solenoid_type': 'Rotativ',
                    'ip_rating': 'IP30',
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Seed WiFi Modules (8 new) ----------
    def _seed_wifi_modules(self, p):
        cat = 'wifi-modules'
        products = [
            {
                'name': 'ESP-01 modul WiFi serial UART',
                'slug': 'esp-01-wifi-serial-uart',
                'sku': 'WIF-00001',
                'manufacturer': 'AI-Thinker',
                'price': 22.00,
                'stock': 180,
                'description': 'Modulul iconic ESP8266 ESP-01 cu interfata UART pentru adaugarea conectivitatii WiFi la orice microcontroler. Foloseste comenzi AT standard si poate fi reflashat cu firmware custom. Optiunea cea mai economica pentru proiecte WiFi.',
                'platforms': ['arduino-uno', 'arduino-mega', 'stm32'],
                'attrs': {
                    'standard': '802.11 b/g/n',
                    'antenna': 'PCB',
                    'interface': 'UART',
                    'tx_power': 20.0,
                    'supply_voltage': 3.3,
                    'range_meters': 50.0,
                }
            },
            {
                'name': 'ESP-WROOM-32 modul WiFi BT antena PCB',
                'slug': 'esp-wroom-32-wifi-bt',
                'sku': 'WIF-00002',
                'manufacturer': 'Espressif',
                'price': 28.50,
                'stock': 150,
                'description': 'Modulul certificat ESP-WROOM-32 cu WiFi 2.4GHz si Bluetooth Classic plus BLE 4.2 integrate. Doua nuclee Xtensa LX6 la 240MHz cu 4MB flash. Folosit ca baza pentru majoritatea placilor de dezvoltare ESP32.',
                'platforms': ['esp32'],
                'attrs': {
                    'standard': '802.11 b/g/n',
                    'antenna': 'PCB',
                    'interface': 'UART/SPI',
                    'tx_power': 20.0,
                    'supply_voltage': 3.3,
                    'range_meters': 100.0,
                }
            },
            {
                'name': 'ESP-07S modul WiFi cu conector IPEX antena externa',
                'slug': 'esp-07s-ipex-external',
                'sku': 'WIF-00003',
                'manufacturer': 'AI-Thinker',
                'price': 32.00,
                'stock': 65,
                'description': 'Variant ESP8266 cu conector IPEX pentru atasarea unei antene externe, asigurand raza marita si penetrare prin pereti. Capsula metalica ecranata pentru emisii reduse. Ideala pentru aplicatii outdoor IoT.',
                'platforms': ['esp8266'],
                'attrs': {
                    'standard': '802.11 b/g/n',
                    'antenna': 'IPEX',
                    'interface': 'UART',
                    'tx_power': 20.5,
                    'supply_voltage': 3.3,
                    'range_meters': 300.0,
                }
            },
            {
                'name': 'ATWINC1500 modul WiFi SPI low-power',
                'slug': 'atwinc1500-spi-low-power',
                'sku': 'WIF-00004',
                'manufacturer': 'Microchip',
                'price': 95.00,
                'stock': 25,
                'description': 'Modul WiFi profesional cu interfata SPI si suport pentru TLS/SSL hardware accelerat. Consum extrem de redus in modul deep sleep, ideal pentru senzori IoT pe baterii. Certificat FCC, CE si IC pentru integrare comerciala.',
                'platforms': ['arduino-uno', 'arduino-mega', 'stm32'],
                'attrs': {
                    'standard': '802.11 b/g/n',
                    'antenna': 'PCB',
                    'interface': 'SPI',
                    'tx_power': 16.0,
                    'supply_voltage': 3.3,
                    'range_meters': 80.0,
                }
            },
            {
                'name': 'RN-XV WiFly modul XBee compatible',
                'slug': 'rn-xv-wifly-xbee',
                'sku': 'WIF-00005',
                'manufacturer': 'Roving Networks',
                'price': 145.00,
                'stock': 18,
                'description': 'Modul WiFi in format XBee compatibil cu socluri standard pentru integrare rapida in proiecte existente. Suport TCP/IP integrat si modul de configurare prin telnet. Folosit in sisteme legacy si proiecte educationale.',
                'platforms': ['arduino-uno', 'arduino-mega'],
                'attrs': {
                    'standard': '802.11 b/g',
                    'antenna': 'Externa',
                    'interface': 'UART',
                    'tx_power': 12.0,
                    'supply_voltage': 3.3,
                    'range_meters': 100.0,
                }
            },
            {
                'name': 'ESP32-WROVER cu PSRAM 8MB',
                'slug': 'esp32-wrover-8mb-psram',
                'sku': 'WIF-00006',
                'manufacturer': 'Espressif',
                'price': 42.00,
                'stock': 80,
                'description': 'Variant ESP-WROOM-32 cu PSRAM extern de 8MB pentru aplicatii care necesita buffer-e mari de memorie. Ideal pentru proiecte cu display TFT mare, audio streaming sau procesare imagine. Pin-out compatibil cu WROOM-32.',
                'platforms': ['esp32'],
                'attrs': {
                    'standard': '802.11 b/g/n',
                    'antenna': 'PCB',
                    'interface': 'UART/SPI',
                    'tx_power': 19.5,
                    'supply_voltage': 3.3,
                    'range_meters': 100.0,
                }
            },
            {
                'name': 'CC3000 modul WiFi Texas Instruments',
                'slug': 'cc3000-wifi-ti',
                'sku': 'WIF-00007',
                'manufacturer': 'Texas Instruments',
                'price': 78.00,
                'stock': 22,
                'description': 'Modul WiFi self-contained de la Texas Instruments cu stiva TCP/IP completa pe chip. Configurare simpla prin SmartConfig direct de pe telefon. Folosit in solutii industriale embedded de generatie veche.',
                'platforms': ['arduino-uno', 'arduino-mega', 'stm32'],
                'attrs': {
                    'standard': '802.11 b/g',
                    'antenna': 'PCB',
                    'interface': 'SPI',
                    'tx_power': 18.0,
                    'supply_voltage': 3.3,
                    'range_meters': 60.0,
                }
            },
            {
                'name': 'RPi WiFi USB nano adapter 150Mbps',
                'slug': 'rpi-wifi-usb-nano-150',
                'sku': 'WIF-00008',
                'manufacturer': 'Edimax',
                'price': 48.00,
                'stock': 95,
                'description': 'Adaptor USB WiFi compatibil cu Raspberry Pi si toate distributiile Linux moderne. Driver inclus in kernel-ul standard, plug-and-play. Solutie excelenta pentru placi RPi mai vechi fara WiFi integrat.',
                'platforms': ['raspberry-pi'],
                'attrs': {
                    'standard': '802.11 b/g/n',
                    'antenna': 'PCB',
                    'interface': 'USB',
                    'tx_power': 17.0,
                    'supply_voltage': 5.0,
                    'range_meters': 50.0,
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Seed Bluetooth Modules (8 new) ----------
    def _seed_bluetooth_modules(self, p):
        cat = 'bluetooth-modules'
        products = [
            {
                'name': 'HC-05 modul Bluetooth Classic SPP',
                'slug': 'hc-05-bluetooth-spp',
                'sku': 'BLT-00001',
                'manufacturer': 'AI-Thinker',
                'price': 26.50,
                'stock': 200,
                'description': 'Cel mai popular modul Bluetooth Classic pentru proiecte Arduino, suportand profil SPP pentru comunicare seriala wireless. Poate functiona ca master sau slave, configurabil prin comenzi AT. Folosit in zeci de mii de tutoriale si proiecte hobby.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32', 'stm32'],
                'attrs': {
                    'bt_version': '2.0 EDR',
                    'profile': 'SPP',
                    'interface': 'UART',
                    'range_meters': 10.0,
                    'supply_voltage': 3.3,
                    'tx_power': 4.0,
                }
            },
            {
                'name': 'HC-06 modul Bluetooth slave only',
                'slug': 'hc-06-bluetooth-slave',
                'sku': 'BLT-00002',
                'manufacturer': 'AI-Thinker',
                'price': 22.00,
                'stock': 150,
                'description': 'Varianta slave-only a popularului HC-05, mai economica pentru aplicatii unde modulul doar primeste conexiuni. Configurare simplificata prin AT. Optiune populara in robotii Arduino controlati de telefon.',
                'platforms': ['arduino-uno', 'arduino-mega', 'stm32'],
                'attrs': {
                    'bt_version': '2.0 EDR',
                    'profile': 'SPP',
                    'interface': 'UART',
                    'range_meters': 10.0,
                    'supply_voltage': 3.3,
                    'tx_power': 4.0,
                }
            },
            {
                'name': 'HM-10 modul Bluetooth Low Energy 4.0',
                'slug': 'hm-10-bluetooth-ble-4',
                'sku': 'BLT-00003',
                'manufacturer': 'JNHuaMao',
                'price': 38.00,
                'stock': 90,
                'description': 'Modul BLE 4.0 compatibil cu iOS si Android pentru aplicatii moderne IoT. Comunicare seriala simpla cu setari AT. Folosit in beacon-uri, dispozitive wearable si controlere pentru smart home.',
                'platforms': ['arduino-uno', 'esp32', 'stm32'],
                'attrs': {
                    'bt_version': '4.0 BLE',
                    'profile': 'GATT custom',
                    'interface': 'UART',
                    'range_meters': 30.0,
                    'supply_voltage': 3.3,
                    'tx_power': 0.0,
                }
            },
            {
                'name': 'JDY-08 modul BLE compact',
                'slug': 'jdy-08-ble-compact',
                'sku': 'BLT-00004',
                'manufacturer': 'JDY',
                'price': 18.50,
                'stock': 110,
                'description': 'Modul Bluetooth Low Energy compact si economic, alternativa la HM-10. Suporta profile GATT custom si advertising configurabil. Ideal pentru proiecte IoT cu buget redus si dispozitive purtabile.',
                'platforms': ['arduino-uno', 'esp32', 'stm32'],
                'attrs': {
                    'bt_version': '4.0 BLE',
                    'profile': 'GATT custom',
                    'interface': 'UART',
                    'range_meters': 20.0,
                    'supply_voltage': 3.3,
                    'tx_power': 0.0,
                }
            },
            {
                'name': 'nRF52840 USB Dongle Bluetooth 5.0',
                'slug': 'nrf52840-usb-dongle-bt5',
                'sku': 'BLT-00005',
                'manufacturer': 'Nordic Semiconductor',
                'price': 88.00,
                'stock': 35,
                'description': 'Dongle USB cu nRF52840 pentru sniffing Bluetooth, dezvoltare BLE 5.0 si Bluetooth Mesh. Suporta multiple protocoale wireless si include radio 802.15.4 pentru Zigbee si Thread. Ideal pentru cercetare si dezvoltare avansata.',
                'platforms': ['raspberry-pi'],
                'attrs': {
                    'bt_version': '5.0',
                    'profile': 'GATT, Mesh',
                    'interface': 'USB',
                    'range_meters': 100.0,
                    'supply_voltage': 5.0,
                    'tx_power': 8.0,
                }
            },
            {
                'name': 'AT-09 BLE 4.0 cu CC2541 chip TI',
                'slug': 'at-09-ble-cc2541',
                'sku': 'BLT-00006',
                'manufacturer': 'Texas Instruments',
                'price': 32.00,
                'stock': 70,
                'description': 'Modul BLE bazat pe popularul chip CC2541 de la Texas Instruments. Compatibil cu HM-10 prin firmware si folosit ca alternativa low-cost. Suport pentru iBeacon si servicii GATT personalizate.',
                'platforms': ['arduino-uno', 'esp32'],
                'attrs': {
                    'bt_version': '4.0 BLE',
                    'profile': 'iBeacon, GATT',
                    'interface': 'UART',
                    'range_meters': 25.0,
                    'supply_voltage': 3.3,
                    'tx_power': 0.0,
                }
            },
            {
                'name': 'KCX_BT_EMITTER modul audio A2DP',
                'slug': 'kcx-bt-emitter-a2dp',
                'sku': 'BLT-00007',
                'manufacturer': 'KCX',
                'price': 45.00,
                'stock': 50,
                'description': 'Modul Bluetooth pentru transmiterea audio stereo prin profil A2DP de la o sursa audio analogica catre casti Bluetooth. Configurare automata fara microcontroler. Ideal pentru retrofit-ul echipamentelor audio vechi.',
                'platforms': [],
                'attrs': {
                    'bt_version': '5.0',
                    'profile': 'A2DP',
                    'interface': 'Audio analog',
                    'range_meters': 15.0,
                    'supply_voltage': 5.0,
                    'tx_power': 4.0,
                }
            },
            {
                'name': 'USB Bluetooth 5.0 dongle CSR pentru RPi',
                'slug': 'usb-bluetooth-5-csr-rpi',
                'sku': 'BLT-00008',
                'manufacturer': 'CSR',
                'price': 28.00,
                'stock': 120,
                'description': 'Adaptor USB Bluetooth 5.0 compatibil cu Linux, ideal pentru a adauga Bluetooth la Raspberry Pi mai vechi sau a inlocui modulul defect. Plug-and-play cu bluez. Suport pentru BLE si Classic.',
                'platforms': ['raspberry-pi'],
                'attrs': {
                    'bt_version': '5.0',
                    'profile': 'A2DP, HID, SPP',
                    'interface': 'USB',
                    'range_meters': 20.0,
                    'supply_voltage': 5.0,
                    'tx_power': 4.0,
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Seed LoRa Modules (8 new) ----------
    def _seed_lora_modules(self, p):
        cat = 'lora-modules'
        products = [
            {
                'name': 'SX1278 modul LoRa 433MHz Ra-02',
                'slug': 'sx1278-lora-433-ra02',
                'sku': 'LOR-00001',
                'manufacturer': 'AI-Thinker',
                'price': 35.00,
                'stock': 95,
                'description': 'Modul LoRa popular bazat pe chipsetul Semtech SX1278 pentru banda libera 433MHz. Comunicare SPI cu microcontrolere si raza ce poate atinge cativa kilometri in spatiu deschis. Folosit in retele IoT distribuite.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32', 'stm32'],
                'attrs': {
                    'frequency': 433.0,
                    'tx_power': 20.0,
                    'sensitivity': -148.0,
                    'interface': 'SPI',
                    'range_km': 5.0,
                    'supply_voltage': 3.3,
                    'spreading_factor': 'SF6-SF12',
                }
            },
            {
                'name': 'SX1276 modul LoRa 868MHz EU',
                'slug': 'sx1276-lora-868-eu',
                'sku': 'LOR-00002',
                'manufacturer': 'Semtech',
                'price': 42.00,
                'stock': 75,
                'description': 'Modul LoRa pe banda europeana de 868MHz, conforma reglementarilor ETSI. Ideal pentru aplicatii LoRaWAN si retele The Things Network. Antena SMA pentru flexibilitate maxima de instalare.',
                'platforms': ['arduino-uno', 'esp32', 'stm32'],
                'attrs': {
                    'frequency': 868.0,
                    'tx_power': 17.0,
                    'sensitivity': -148.0,
                    'interface': 'SPI',
                    'range_km': 10.0,
                    'supply_voltage': 3.3,
                    'spreading_factor': 'SF7-SF12',
                }
            },
            {
                'name': 'RFM95W modul LoRa HopeRF 915MHz',
                'slug': 'rfm95w-lora-915',
                'sku': 'LOR-00003',
                'manufacturer': 'HopeRF',
                'price': 48.00,
                'stock': 55,
                'description': 'Modul LoRa de inalta calitate bazat pe SX1276 pentru banda 915MHz folosita in America. Format compact si pinout standardizat folosit in placile Adafruit Feather LoRa. Ideal pentru sezatoare wireless de lunga distanta.',
                'platforms': ['arduino-uno', 'esp32', 'stm32'],
                'attrs': {
                    'frequency': 915.0,
                    'tx_power': 20.0,
                    'sensitivity': -148.0,
                    'interface': 'SPI',
                    'range_km': 8.0,
                    'supply_voltage': 3.3,
                    'spreading_factor': 'SF7-SF12',
                }
            },
            {
                'name': 'LoRa-E5 modul STM32WL integrat',
                'slug': 'lora-e5-stm32wl',
                'sku': 'LOR-00004',
                'manufacturer': 'Seeed',
                'price': 89.00,
                'stock': 35,
                'description': 'Solutie all-in-one combinand STM32WLE5 cu transceiver LoRa pe acelasi chip. Firmware AT inclus si suport LoRaWAN preprogramat. Reduce semnificativ complexitatea designului hardware pentru aplicatii LPWAN.',
                'platforms': ['stm32'],
                'attrs': {
                    'frequency': 868.0,
                    'tx_power': 22.0,
                    'sensitivity': -148.0,
                    'interface': 'UART',
                    'range_km': 15.0,
                    'supply_voltage': 3.3,
                    'spreading_factor': 'SF5-SF12',
                }
            },
            {
                'name': 'Heltec WiFi LoRa 32 V3 placa dezvoltare',
                'slug': 'heltec-wifi-lora-32-v3',
                'sku': 'LOR-00005',
                'manufacturer': 'Heltec',
                'price': 165.00,
                'stock': 28,
                'description': 'Placa de dezvoltare cu ESP32-S3, modul LoRa SX1262 si display OLED integrate. Ideal pentru prototipuri rapide de noduri LoRa cu interfata utilizator. Include incarcator USB-C si conector pentru baterie LiPo.',
                'platforms': ['esp32'],
                'attrs': {
                    'frequency': 868.0,
                    'tx_power': 22.0,
                    'sensitivity': -148.0,
                    'interface': 'SPI',
                    'range_km': 12.0,
                    'supply_voltage': 3.3,
                    'spreading_factor': 'SF5-SF12',
                }
            },
            {
                'name': 'LLCC68 modul LoRa pret redus 433MHz',
                'slug': 'llcc68-lora-budget-433',
                'sku': 'LOR-00006',
                'manufacturer': 'Semtech',
                'price': 24.00,
                'stock': 80,
                'description': 'Versiune cost-redus a SX1262 cu suport limitat la SF5-SF11 dar pastrand sensibilitatea ridicata. Ideal pentru aplicatii batch unde bugetul este critic. Pin-compatibil cu SX1262.',
                'platforms': ['arduino-uno', 'esp32', 'stm32'],
                'attrs': {
                    'frequency': 433.0,
                    'tx_power': 22.0,
                    'sensitivity': -146.0,
                    'interface': 'SPI',
                    'range_km': 6.0,
                    'supply_voltage': 3.3,
                    'spreading_factor': 'SF5-SF11',
                }
            },
            {
                'name': 'EBYTE E32-433T30D modul LoRa cu UART',
                'slug': 'ebyte-e32-433-uart',
                'sku': 'LOR-00007',
                'manufacturer': 'EBYTE',
                'price': 78.00,
                'stock': 45,
                'description': 'Modul LoRa cu interfata UART simplificata si firmware integrat care abstractizeaza protocolul radio. Putere ridicata de 1W pentru raza maxima si setari prin pini hardware. Folosit larg in telemetrie agricola si statii meteo izolate.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32'],
                'attrs': {
                    'frequency': 433.0,
                    'tx_power': 30.0,
                    'sensitivity': -147.0,
                    'interface': 'UART',
                    'range_km': 8.0,
                    'supply_voltage': 5.0,
                    'spreading_factor': 'SF7-SF12',
                }
            },
            {
                'name': 'RAK4631 Wisblock LoRa nRF52840',
                'slug': 'rak4631-wisblock-lora',
                'sku': 'LOR-00008',
                'manufacturer': 'RAKwireless',
                'price': 245.00,
                'stock': 18,
                'description': 'Modul LoRa profesional pentru ecosistemul Wisblock cu nRF52840 si SX1262 integrate. Suport pentru Meshtastic si LoRaWAN out-of-the-box. Folosit in proiecte profesionale de senzori IoT distribuite.',
                'platforms': ['stm32'],
                'attrs': {
                    'frequency': 868.0,
                    'tx_power': 22.0,
                    'sensitivity': -148.0,
                    'interface': 'SPI',
                    'range_km': 15.0,
                    'supply_voltage': 3.3,
                    'spreading_factor': 'SF5-SF12',
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Seed RS485 Modules (8 new) ----------
    def _seed_rs485_modules(self, p):
        cat = 'rs485-modules'
        products = [
            {
                'name': 'MAX485 modul convertor TTL la RS485',
                'slug': 'max485-ttl-rs485',
                'sku': 'RS4-00001',
                'manufacturer': 'Maxim Integrated',
                'price': 12.50,
                'stock': 250,
                'description': 'Modul economic bazat pe IC-ul MAX485 pentru conversia comunicatiei TTL la RS485 half-duplex. Controlul directiei prin pin DE/RE. Optiunea cea mai populara pentru proiecte Modbus simple cu Arduino si ESP.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp8266', 'esp32', 'stm32'],
                'attrs': {
                    'interface': 'TTL UART',
                    'baud_rate': 115200,
                    'isolation': 'Fara izolatie',
                    'node_count': 32,
                    'supply_voltage': 5.0,
                    'protection': 'ESD plus-minus 15kV',
                }
            },
            {
                'name': 'ADM2587E modul RS485 izolat galvanic',
                'slug': 'adm2587e-isolated-rs485',
                'sku': 'RS4-00002',
                'manufacturer': 'Analog Devices',
                'price': 165.00,
                'stock': 22,
                'description': 'Convertor RS485 cu izolatie galvanica integrata de 2.5kV pentru protectia microcontrolerului de tranzitii ale tensiunii pe linia de comunicatii. Esential in medii industriale cu zgomot electromagnetic ridicat.',
                'platforms': ['arduino-mega', 'stm32', 'plc-siemens-s7'],
                'attrs': {
                    'interface': 'TTL UART',
                    'baud_rate': 500000,
                    'isolation': '2.5kV izolat',
                    'node_count': 256,
                    'supply_voltage': 5.0,
                    'protection': 'ESD plus-minus 15kV',
                }
            },
            {
                'name': 'USB to RS485 FTDI cu izolatie',
                'slug': 'usb-rs485-ftdi-isolated',
                'sku': 'RS4-00003',
                'manufacturer': 'FTDI',
                'price': 145.00,
                'stock': 35,
                'description': 'Convertor USB la RS485 cu chip FTDI FT232 si izolatie galvanica integrata. Folosit pentru depanare retele Modbus si comunicare cu PLC-uri direct de pe laptop. Driver inclus in Windows si Linux.',
                'platforms': ['raspberry-pi'],
                'attrs': {
                    'interface': 'USB',
                    'baud_rate': 921600,
                    'isolation': '1kV izolat',
                    'node_count': 128,
                    'supply_voltage': 5.0,
                    'protection': 'ESD plus-minus 15kV',
                }
            },
            {
                'name': 'SP3485 modul mini RS485 3.3V',
                'slug': 'sp3485-mini-rs485-3v3',
                'sku': 'RS4-00004',
                'manufacturer': 'MaxLinear',
                'price': 18.00,
                'stock': 110,
                'description': 'Modul RS485 alimentat la 3.3V compatibil direct cu ESP32, STM32 si alte MCU low-voltage. Nu necesita level shifter, simplificand designul. Half-duplex cu rate de transfer pana la 10Mbps.',
                'platforms': ['esp32', 'stm32'],
                'attrs': {
                    'interface': 'TTL UART 3.3V',
                    'baud_rate': 10000000,
                    'isolation': 'Fara izolatie',
                    'node_count': 32,
                    'supply_voltage': 3.3,
                    'protection': 'ESD plus-minus 8kV',
                }
            },
            {
                'name': 'Modbus RS485 4 intrari digitale modul',
                'slug': 'modbus-rs485-4di-module',
                'sku': 'RS4-00005',
                'manufacturer': 'Eletechsup',
                'price': 195.00,
                'stock': 25,
                'description': 'Modul Modbus RTU cu 4 intrari digitale optoizolate si comunicare RS485. Configurare adresa prin DIP switches. Folosit in achizitie de date industriala si monitorizarea senzorilor digitali distribuiti.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'interface': 'RS485 Modbus RTU',
                    'baud_rate': 38400,
                    'isolation': '3kV izolat',
                    'node_count': 247,
                    'supply_voltage': 24.0,
                    'protection': 'IP20, ESD plus-minus 15kV',
                }
            },
            {
                'name': 'Convertor RS485 la Ethernet TCP Modbus',
                'slug': 'rs485-ethernet-modbus-tcp',
                'sku': 'RS4-00006',
                'manufacturer': 'USR IoT',
                'price': 285.00,
                'stock': 18,
                'description': 'Convertor protocol bidirectional intre Modbus RTU (RS485) si Modbus TCP (Ethernet) pentru integrarea senzorilor industriali in retele moderne IT. Suporta multiple sloturi master/slave. Configurare prin pagina web.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley', 'raspberry-pi'],
                'attrs': {
                    'interface': 'RS485 / Ethernet',
                    'baud_rate': 115200,
                    'isolation': '2kV izolat',
                    'node_count': 32,
                    'supply_voltage': 24.0,
                    'protection': 'IP30',
                }
            },
            {
                'name': 'MAX13487E modul RS485 auto-direction',
                'slug': 'max13487e-auto-direction',
                'sku': 'RS4-00007',
                'manufacturer': 'Maxim Integrated',
                'price': 35.00,
                'stock': 60,
                'description': 'Convertor RS485 cu functie automata de control directie, eliminand nevoia unui pin DE/RE. Simplifica codul de comunicatie si permite folosirea cu UART standard. Ideal pentru proiecte cu pini GPIO limitati.',
                'platforms': ['arduino-uno', 'esp8266', 'esp32', 'stm32'],
                'attrs': {
                    'interface': 'TTL UART',
                    'baud_rate': 500000,
                    'isolation': 'Fara izolatie',
                    'node_count': 256,
                    'supply_voltage': 5.0,
                    'protection': 'ESD plus-minus 15kV',
                }
            },
            {
                'name': 'Shield Arduino RS485 cu terminale screw',
                'slug': 'arduino-shield-rs485-screw',
                'sku': 'RS4-00008',
                'manufacturer': 'Linksprite',
                'price': 65.00,
                'stock': 40,
                'description': 'Shield Arduino oficial pentru RS485 cu terminale cu surub si rezistente de terminare comutabile prin jumperi. Compatibil cu Uno, Mega si pin-out standard. Ideal pentru prototipuri industriale rapide.',
                'platforms': ['arduino-uno', 'arduino-mega'],
                'attrs': {
                    'interface': 'TTL UART',
                    'baud_rate': 115200,
                    'isolation': 'Fara izolatie',
                    'node_count': 32,
                    'supply_voltage': 5.0,
                    'protection': 'ESD plus-minus 15kV',
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Seed Raspberry Pi Boards (8 new) ----------
    def _seed_raspberry_pi_boards(self, p):
        cat = 'raspberry-pi-boards'
        products = [
            {
                'name': 'Raspberry Pi 4B 4GB',
                'slug': 'raspberry-pi-4b-4gb',
                'sku': 'RPI-00001',
                'manufacturer': 'Raspberry Pi Foundation',
                'price': 425.00,
                'stock': 45,
                'description': 'Single board computer popular cu CPU quad-core Cortex-A72 si 4GB RAM, ideal pentru proiecte avansate IoT, retro gaming, sau ca server casnic. Suporta dual display 4K si Gigabit Ethernet. USB 3.0 pentru viteza maxima a perifericelor.',
                'platforms': ['raspberry-pi'],
                'attrs': {
                    'cpu': 'BCM2711 quad-core 1.5GHz',
                    'ram': 4,
                    'connectivity': 'WiFi, BT 5.0, Gigabit Ethernet',
                    'usb_ports': 4,
                    'gpio_pins': 40,
                    'max_resolution': '4K 60Hz dual',
                }
            },
            {
                'name': 'Raspberry Pi 5 8GB',
                'slug': 'raspberry-pi-5-8gb',
                'sku': 'RPI-00002',
                'manufacturer': 'Raspberry Pi Foundation',
                'price': 595.00,
                'stock': 30,
                'description': 'Cea mai recenta generatie de Raspberry Pi cu CPU Cortex-A76 quad-core la 2.4GHz, performante de pana la 3x mai mari decat Pi 4. PCIe Gen 2 si chip dedicat I/O pentru viteze marite. Necesita sursa de alimentare USB-C de 5A.',
                'platforms': ['raspberry-pi'],
                'attrs': {
                    'cpu': 'BCM2712 quad-core 2.4GHz',
                    'ram': 8,
                    'connectivity': 'WiFi 5, BT 5.0, Gigabit Ethernet',
                    'usb_ports': 4,
                    'gpio_pins': 40,
                    'max_resolution': '4K 60Hz dual',
                }
            },
            {
                'name': 'Raspberry Pi Zero 2 W',
                'slug': 'raspberry-pi-zero-2-w',
                'sku': 'RPI-00003',
                'manufacturer': 'Raspberry Pi Foundation',
                'price': 95.00,
                'stock': 75,
                'description': 'Versiune mini a Pi 3 cu CPU quad-core la 1GHz si format ultra-compact pentru proiecte purtabile si embedded. WiFi 2.4GHz si Bluetooth integrate. Consum redus ideal pentru dispozitive alimentate pe baterii.',
                'platforms': ['raspberry-pi'],
                'attrs': {
                    'cpu': 'BCM2710A1 quad-core 1GHz',
                    'ram': 1,
                    'connectivity': 'WiFi 2.4GHz, BT 4.2',
                    'usb_ports': 1,
                    'gpio_pins': 40,
                    'max_resolution': '1080p',
                }
            },
            {
                'name': 'Raspberry Pi Pico W cu RP2040',
                'slug': 'raspberry-pi-pico-w-rp2040',
                'sku': 'RPI-00004',
                'manufacturer': 'Raspberry Pi Foundation',
                'price': 36.00,
                'stock': 130,
                'description': 'Microcontroler oficial Raspberry Pi cu chip dual-core ARM RP2040 si WiFi 2.4GHz integrat. Programabil in MicroPython, C/C++ sau CircuitPython. Optiune economica pentru proiecte IoT cu performante surprinzator de bune.',
                'platforms': ['raspberry-pi'],
                'attrs': {
                    'cpu': 'RP2040 dual-core M0+ 133MHz',
                    'ram': 1,
                    'connectivity': 'WiFi 2.4GHz',
                    'usb_ports': 1,
                    'gpio_pins': 26,
                    'max_resolution': 'Fara display',
                }
            },
            {
                'name': 'Raspberry Pi 4B 8GB pentru server',
                'slug': 'raspberry-pi-4b-8gb-server',
                'sku': 'RPI-00005',
                'manufacturer': 'Raspberry Pi Foundation',
                'price': 525.00,
                'stock': 25,
                'description': 'Configuratia top a Pi 4 cu 8GB RAM, ideala pentru proiecte ce ruleaza multiple containere Docker, server NAS sau ca desktop secundar. Performante apropiate de mini PC-uri x86 dedicate.',
                'platforms': ['raspberry-pi'],
                'attrs': {
                    'cpu': 'BCM2711 quad-core 1.5GHz',
                    'ram': 8,
                    'connectivity': 'WiFi, BT 5.0, Gigabit Ethernet',
                    'usb_ports': 4,
                    'gpio_pins': 40,
                    'max_resolution': '4K 60Hz dual',
                }
            },
            {
                'name': 'Raspberry Pi Compute Module 4',
                'slug': 'raspberry-pi-cm4-4gb',
                'sku': 'RPI-00006',
                'manufacturer': 'Raspberry Pi Foundation',
                'price': 385.00,
                'stock': 18,
                'description': 'Versiune industriala embedded a Pi 4 cu format SODIMM si conectori board-to-board pentru integrare in produse comerciale. Disponibil cu eMMC integrat si optiuni WiFi optionale. Folosit larg in NAS-uri si signage profesional.',
                'platforms': ['raspberry-pi'],
                'attrs': {
                    'cpu': 'BCM2711 quad-core 1.5GHz',
                    'ram': 4,
                    'connectivity': 'WiFi optional, Gigabit Ethernet',
                    'usb_ports': 0,
                    'gpio_pins': 28,
                    'max_resolution': '4K 60Hz dual',
                }
            },
            {
                'name': 'Raspberry Pi 3 Model B+',
                'slug': 'raspberry-pi-3-b-plus',
                'sku': 'RPI-00007',
                'manufacturer': 'Raspberry Pi Foundation',
                'price': 245.00,
                'stock': 40,
                'description': 'Generatia anterioara a Pi cu CPU 64-bit quad-core la 1.4GHz si 1GB RAM. Inca foarte capabila pentru proiecte hobby, automatizari domestice si educationale. Compatibil cu majoritatea accesoriilor existente.',
                'platforms': ['raspberry-pi'],
                'attrs': {
                    'cpu': 'BCM2837B0 quad-core 1.4GHz',
                    'ram': 1,
                    'connectivity': 'WiFi dual-band, BT 4.2, Gigabit',
                    'usb_ports': 4,
                    'gpio_pins': 40,
                    'max_resolution': '1080p',
                }
            },
            {
                'name': 'Raspberry Pi Pico fara WiFi',
                'slug': 'raspberry-pi-pico-base',
                'sku': 'RPI-00008',
                'manufacturer': 'Raspberry Pi Foundation',
                'price': 22.00,
                'stock': 200,
                'description': 'Microcontrolerul original RP2040 fara conectivitate wireless, ideal pentru proiecte cu necesitati de procesare locala. PIO programabil unic permite implementarea de protocoale custom hardware-accelerate. Cea mai economica solutie de la Raspberry Pi.',
                'platforms': ['raspberry-pi'],
                'attrs': {
                    'cpu': 'RP2040 dual-core M0+ 133MHz',
                    'ram': 1,
                    'connectivity': 'Fara wireless',
                    'usb_ports': 1,
                    'gpio_pins': 26,
                    'max_resolution': 'Fara display',
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Seed PLC Modules (8 new) ----------
    def _seed_plc_modules(self, p):
        cat = 'plc-modules'
        products = [
            {
                'name': 'Siemens LOGO! 8 12/24RCE',
                'slug': 'siemens-logo-8-12-24rce',
                'sku': 'PLC-00001',
                'manufacturer': 'Siemens',
                'price': 985.00,
                'stock': 22,
                'description': 'Micro-PLC modular din seria LOGO! 8 cu 8 intrari digitale si 4 iesiri pe releu. Programare grafica prin LOGO! Soft Comfort cu functii FBD. Server web integrat pentru monitorizare remote. Ideal pentru automatizari mici industriale si comerciale.',
                'platforms': ['plc-siemens-s7'],
                'attrs': {
                    'cpu': 'Siemens proprietary',
                    'digital_inputs': 8,
                    'digital_outputs': 4,
                    'analog_inputs': 4,
                    'communication': 'Ethernet, web server',
                    'supply_voltage': 24.0,
                    'programming_language': 'FBD/LAD',
                }
            },
            {
                'name': 'Siemens S7-1200 CPU 1214C DC/DC/DC',
                'slug': 'siemens-s7-1200-1214c',
                'sku': 'PLC-00002',
                'manufacturer': 'Siemens',
                'price': 2485.00,
                'stock': 10,
                'description': 'PLC compact din seria S7-1200 cu 14 intrari digitale, 10 iesiri tranzistor si 2 intrari analogice integrate. Programare in TIA Portal cu suport pentru SCL, LAD si FBD. Standard industrial pentru aplicatii de complexitate medie.',
                'platforms': ['plc-siemens-s7'],
                'attrs': {
                    'cpu': 'Siemens S7-1200 CPU 1214C',
                    'digital_inputs': 14,
                    'digital_outputs': 10,
                    'analog_inputs': 2,
                    'communication': 'PROFINET, Modbus TCP',
                    'supply_voltage': 24.0,
                    'programming_language': 'LAD/FBD/SCL',
                }
            },
            {
                'name': 'Allen-Bradley Micro820 controller',
                'slug': 'allen-bradley-micro820',
                'sku': 'PLC-00003',
                'manufacturer': 'Allen-Bradley',
                'price': 1985.00,
                'stock': 12,
                'description': 'PLC compact din familia Micro800 pentru aplicatii de complexitate redusa si medie. Programare in Connected Components Workbench cu suport pentru limbaje IEC 61131-3. Conectivitate Ethernet/IP integrata.',
                'platforms': ['plc-allen-bradley'],
                'attrs': {
                    'cpu': 'Allen-Bradley Micro820',
                    'digital_inputs': 12,
                    'digital_outputs': 7,
                    'analog_inputs': 4,
                    'communication': 'Ethernet/IP',
                    'supply_voltage': 24.0,
                    'programming_language': 'LAD/FBD/ST',
                }
            },
            {
                'name': 'Schneider Modicon M221 24I/O',
                'slug': 'schneider-modicon-m221-24io',
                'sku': 'PLC-00004',
                'manufacturer': 'Schneider Electric',
                'price': 1685.00,
                'stock': 15,
                'description': 'PLC din gama Modicon M221 cu 14 intrari digitale si 10 iesiri tranzistor. Programare in EcoStruxure Machine Expert Basic gratuit. Comunicare Modbus TCP, serial si Ethernet. Foarte popular in industria de mid-range.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'cpu': 'Schneider M221',
                    'digital_inputs': 14,
                    'digital_outputs': 10,
                    'analog_inputs': 2,
                    'communication': 'Modbus TCP/RTU, Ethernet',
                    'supply_voltage': 24.0,
                    'programming_language': 'LAD/IL/ST',
                }
            },
            {
                'name': 'Wago 750-880 PLC ETHERNET',
                'slug': 'wago-750-880-ethernet',
                'sku': 'PLC-00005',
                'manufacturer': 'Wago',
                'price': 2245.00,
                'stock': 8,
                'description': 'Controller PLC modular Wago cu interfata Ethernet dubla si suport pentru zeci de module I/O conectabile. Programare in CODESYS cu librarie completa de functii. Folosit larg in automatizari de cladiri si SCADA.',
                'platforms': ['plc-siemens-s7'],
                'attrs': {
                    'cpu': 'Wago 750-880 ARM Cortex',
                    'digital_inputs': 0,
                    'digital_outputs': 0,
                    'analog_inputs': 0,
                    'communication': 'Ethernet dual, MQTT, OPC UA',
                    'supply_voltage': 24.0,
                    'programming_language': 'CODESYS IEC 61131-3',
                }
            },
            {
                'name': 'Mitsubishi FX5U-32MT compact PLC',
                'slug': 'mitsubishi-fx5u-32mt',
                'sku': 'PLC-00006',
                'manufacturer': 'Mitsubishi',
                'price': 1845.00,
                'stock': 14,
                'description': 'PLC compact din seria iQ-F cu 16 intrari digitale si 16 iesiri tranzistor. Programare in GX Works3 cu performante de procesare ridicate. Suport built-in pentru control motoare pas cu pas si servo.',
                'platforms': ['plc-allen-bradley'],
                'attrs': {
                    'cpu': 'Mitsubishi FX5U',
                    'digital_inputs': 16,
                    'digital_outputs': 16,
                    'analog_inputs': 2,
                    'communication': 'Ethernet, CC-Link, RS-485',
                    'supply_voltage': 24.0,
                    'programming_language': 'LAD/ST/FBD',
                }
            },
            {
                'name': 'OpenPLC USB modul educational',
                'slug': 'openplc-usb-educational',
                'sku': 'PLC-00007',
                'manufacturer': 'OpenPLC',
                'price': 485.00,
                'stock': 25,
                'description': 'PLC open-source bazat pe Arduino cu firmware OpenPLC conform IEC 61131-3. Ideal pentru educatie si laboratoare de automatizari. Programare in ladder gratuit prin OpenPLC Editor. Suport ModbusTCP si DNP3.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'cpu': 'Arduino MEGA 2560',
                    'digital_inputs': 24,
                    'digital_outputs': 16,
                    'analog_inputs': 8,
                    'communication': 'USB, Ethernet (optional)',
                    'supply_voltage': 24.0,
                    'programming_language': 'Ladder (LAD)',
                }
            },
            {
                'name': 'Siemens ET 200SP IM 155-6 PN HF',
                'slug': 'siemens-et-200sp-im-155-6',
                'sku': 'PLC-00008',
                'manufacturer': 'Siemens',
                'price': 1850.00,
                'stock': 6,
                'description': 'Modul interface pentru sistem distribuit ET 200SP cu conectivitate PROFINET de inalta performanta. Permite extinderea unui PLC central cu I/O remote. Folosit in instalatii industriale mari cu zone separate.',
                'platforms': ['plc-siemens-s7'],
                'attrs': {
                    'cpu': 'Siemens IM 155-6',
                    'digital_inputs': 0,
                    'digital_outputs': 0,
                    'analog_inputs': 0,
                    'communication': 'PROFINET HF dual',
                    'supply_voltage': 24.0,
                    'programming_language': 'TIA Portal',
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Seed DIN Rail PSU (8 new) ----------
    def _seed_din_rail_psu(self, p):
        cat = 'din-rail-psu'
        products = [
            {
                'name': 'Mean Well DR-15-12 sursa DIN 15W 12V',
                'slug': 'mean-well-dr-15-12',
                'sku': 'DIN-00001',
                'manufacturer': 'Mean Well',
                'price': 115.00,
                'stock': 60,
                'description': 'Sursa de alimentare comutata pentru montaj pe sina DIN cu putere de 15W si iesire 12V/1.25A. Eficienta ridicata si format compact. Ideala pentru alimentarea senzorilor industriali si dispozitivelor de automatizare cu consum redus.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'input_voltage': (85, 264),
                    'output_voltage': 12.0,
                    'output_current': 1.25,
                    'output_power': 15.0,
                    'efficiency': 86.0,
                    'protection': 'OVP, OCP, SCP, OTP',
                }
            },
            {
                'name': 'Mean Well DR-60-24 sursa DIN 60W 24V',
                'slug': 'mean-well-dr-60-24',
                'sku': 'DIN-00002',
                'manufacturer': 'Mean Well',
                'price': 245.00,
                'stock': 45,
                'description': 'Sursa industriala de 60W cu iesire 24V/2.5A pentru aplicatii PLC si automatizari medii. Montaj pe sina DIN TS35 si terminale cu surub. Compatibilitate EMC industriala pentru medii dure.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'input_voltage': (85, 264),
                    'output_voltage': 24.0,
                    'output_current': 2.5,
                    'output_power': 60.0,
                    'efficiency': 88.0,
                    'protection': 'OVP, OCP, SCP, OTP',
                }
            },
            {
                'name': 'Mean Well HDR-15-5 ultra slim 5V',
                'slug': 'mean-well-hdr-15-5',
                'sku': 'DIN-00003',
                'manufacturer': 'Mean Well',
                'price': 95.00,
                'stock': 75,
                'description': 'Sursa DIN ultra-slim de doar 17.5mm latime, ideala pentru cabinete electrice cu spatiu redus. Iesire 5V/2.4A pentru alimentarea Raspberry Pi, ESP32 si alte placi de dezvoltare in mediu industrial.',
                'platforms': ['raspberry-pi', 'esp32'],
                'attrs': {
                    'input_voltage': (85, 264),
                    'output_voltage': 5.0,
                    'output_current': 2.4,
                    'output_power': 15.0,
                    'efficiency': 80.0,
                    'protection': 'OVP, SCP',
                }
            },
            {
                'name': 'Mean Well DR-120-24 sursa 120W',
                'slug': 'mean-well-dr-120-24',
                'sku': 'DIN-00004',
                'manufacturer': 'Mean Well',
                'price': 425.00,
                'stock': 28,
                'description': 'Sursa industriala de 120W cu iesire 24V/5A pentru aplicatii cu consum mediu-mare. Garantata pentru 100000 ore MTBF in conditii normale. Certificari UL, CB si CE pentru integrare globala.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'input_voltage': (88, 264),
                    'output_voltage': 24.0,
                    'output_current': 5.0,
                    'output_power': 120.0,
                    'efficiency': 89.0,
                    'protection': 'OVP, OCP, SCP, OTP',
                }
            },
            {
                'name': 'Phoenix Contact QUINT 24V 240W redundanta',
                'slug': 'phoenix-quint-24v-240w',
                'sku': 'DIN-00005',
                'manufacturer': 'Phoenix Contact',
                'price': 1485.00,
                'stock': 10,
                'description': 'Sursa premium industriala cu putere de 240W si tehnologie SFB pentru tripla curent nominal pe scurt timp. Functii integrate de diagnoza si comunicare preventiva. Folosita in instalatii critice care necesita fiabilitate maxima.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'input_voltage': (100, 240),
                    'output_voltage': 24.0,
                    'output_current': 10.0,
                    'output_power': 240.0,
                    'efficiency': 94.0,
                    'protection': 'SFB, diagnostic LED, signal',
                }
            },
            {
                'name': 'Siemens SITOP PSU100S 24V 5A',
                'slug': 'siemens-sitop-psu100s-24v-5a',
                'sku': 'DIN-00006',
                'manufacturer': 'Siemens',
                'price': 685.00,
                'stock': 18,
                'description': 'Sursa Siemens SITOP de calitate industriala dovedita, ideala pentru aplicatii cu PLC Siemens S7. Comutare la 5A cu reglare precisa de tensiune. Compatibila perfect cu eco-sistemul TIA Portal.',
                'platforms': ['plc-siemens-s7'],
                'attrs': {
                    'input_voltage': (85, 264),
                    'output_voltage': 24.0,
                    'output_current': 5.0,
                    'output_power': 120.0,
                    'efficiency': 91.0,
                    'protection': 'OVP, OCP, SCP, OTP',
                }
            },
            {
                'name': 'Mean Well NDR-240-48 industrial 48V',
                'slug': 'mean-well-ndr-240-48',
                'sku': 'DIN-00007',
                'manufacturer': 'Mean Well',
                'price': 685.00,
                'stock': 14,
                'description': 'Sursa industriala de 240W cu iesire 48V/5A, ideala pentru alimentarea servo-drive-urilor mici si retelelor industriale PoE. Boost de 150 procente putere pana la 3 secunde. Constructie robusta pentru medii cu vibratii.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'input_voltage': (90, 264),
                    'output_voltage': 48.0,
                    'output_current': 5.0,
                    'output_power': 240.0,
                    'efficiency': 91.0,
                    'protection': 'OVP, OCP, SCP, OTP',
                }
            },
            {
                'name': 'Omron S8VK-G06024 sursa 60W 24V',
                'slug': 'omron-s8vk-g06024',
                'sku': 'DIN-00008',
                'manufacturer': 'Omron',
                'price': 295.00,
                'stock': 30,
                'description': 'Sursa Omron compacta de 60W cu iesire stabila 24V/2.5A si protectii multiple. Format mai mic decat majoritatea concurentei pentru economie de spatiu pe sina DIN. Garantata 10 ani fabricant.',
                'platforms': ['plc-siemens-s7', 'plc-allen-bradley'],
                'attrs': {
                    'input_voltage': (85, 264),
                    'output_voltage': 24.0,
                    'output_current': 2.5,
                    'output_power': 60.0,
                    'efficiency': 89.0,
                    'protection': 'OVP, OCP, SCP, OTP',
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)

    # ---------- Seed DC-DC Converters (8 new) ----------
    def _seed_dc_dc_converters(self, p):
        cat = 'dc-dc-converters'
        products = [
            {
                'name': 'LM2596 modul step-down ajustabil',
                'slug': 'lm2596-buck-adjustable',
                'sku': 'DCC-00001',
                'manufacturer': 'Texas Instruments',
                'price': 9.50,
                'stock': 300,
                'description': 'Cel mai popular convertor step-down (buck) cu iesire reglabila prin potentiometru intre 1.25V si 35V. Curent maxim de 3A cu eficienta tipica de 80 procente. Modulul de baza in zeci de mii de proiecte hobby si educationale.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp8266', 'esp32', 'raspberry-pi', 'stm32'],
                'attrs': {
                    'input_range': (4.5, 40),
                    'output_voltage': 5.0,
                    'max_current': 3.0,
                    'converter_type': 'Buck',
                    'efficiency': 80.0,
                    'supply_voltage': 12.0,
                }
            },
            {
                'name': 'MT3608 modul step-up boost 2A',
                'slug': 'mt3608-boost-2a',
                'sku': 'DCC-00002',
                'manufacturer': 'Aerosemi',
                'price': 8.50,
                'stock': 250,
                'description': 'Convertor step-up (boost) compact pentru cresterea tensiunii de la baterii LiPo (3.7V) la 5V sau mai mult. Reglare prin trimmer si curent de iesire pana la 2A. Folosit larg in proiecte portabile alimentate pe baterii.',
                'platforms': ['arduino-uno', 'esp8266', 'esp32'],
                'attrs': {
                    'input_range': (2, 24),
                    'output_voltage': 5.0,
                    'max_current': 2.0,
                    'converter_type': 'Boost',
                    'efficiency': 93.0,
                    'supply_voltage': 3.7,
                }
            },
            {
                'name': 'XL4015 modul buck 5A current high',
                'slug': 'xl4015-buck-5a',
                'sku': 'DCC-00003',
                'manufacturer': 'XLSEMI',
                'price': 18.50,
                'stock': 130,
                'description': 'Convertor buck de mare curent pana la 5A cu eficienta de 96 procente. Include capacitate de reglare a curentului pentru aplicatii de incarcator baterii. Radiator integrat pentru disiparea termica.',
                'platforms': ['arduino-uno', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'input_range': (5, 32),
                    'output_voltage': 5.0,
                    'max_current': 5.0,
                    'converter_type': 'Buck',
                    'efficiency': 96.0,
                    'supply_voltage': 12.0,
                }
            },
            {
                'name': 'XL6009 modul buck-boost 4A',
                'slug': 'xl6009-buck-boost-4a',
                'sku': 'DCC-00004',
                'manufacturer': 'XLSEMI',
                'price': 16.50,
                'stock': 140,
                'description': 'Convertor buck-boost care poate creste sau scadea tensiunea de intrare, ideal pentru aplicatii cu baterii care variaza tensiunea. Curent de iesire pana la 4A si reglare prin trimmer. Stabilitate excelenta la sarcina.',
                'platforms': ['arduino-uno', 'esp32'],
                'attrs': {
                    'input_range': (5, 32),
                    'output_voltage': 12.0,
                    'max_current': 4.0,
                    'converter_type': 'Buck-Boost',
                    'efficiency': 94.0,
                    'supply_voltage': 12.0,
                }
            },
            {
                'name': 'AMS1117 LDO 3.3V regulator linear',
                'slug': 'ams1117-3v3-ldo',
                'sku': 'DCC-00005',
                'manufacturer': 'Advanced Monolithic Systems',
                'price': 6.50,
                'stock': 400,
                'description': 'Regulator linear LDO clasic pentru iesire 3.3V din intrare 5V. Curent maxim 1A si dropout redus. Ideal pentru alimentarea modulelor ESP-01 si altor periferice 3.3V direct de la USB.',
                'platforms': ['arduino-uno', 'esp8266', 'esp32'],
                'attrs': {
                    'input_range': (4.7, 12),
                    'output_voltage': 3.3,
                    'max_current': 1.0,
                    'converter_type': 'Buck',
                    'efficiency': 66.0,
                    'supply_voltage': 5.0,
                }
            },
            {
                'name': 'DPS5005 sursa programabila digitala 50V 5A',
                'slug': 'dps5005-programmable-50v-5a',
                'sku': 'DCC-00006',
                'manufacturer': 'RuiDeng',
                'price': 285.00,
                'stock': 25,
                'description': 'Sursa de banc digitala programabila cu display color si encoder. Iesire reglabila pana la 50V si 5A cu citire precisa de tensiune, curent si putere. Optional cu modul comunicatie WiFi/Bluetooth pentru monitorizare remote.',
                'platforms': [],
                'attrs': {
                    'input_range': (6, 55),
                    'output_voltage': 24.0,
                    'max_current': 5.0,
                    'converter_type': 'Buck',
                    'efficiency': 92.0,
                    'supply_voltage': 48.0,
                }
            },
            {
                'name': 'TPS5430 buck 3A SOT223 placa',
                'slug': 'tps5430-buck-3a-sot223',
                'sku': 'DCC-00007',
                'manufacturer': 'Texas Instruments',
                'price': 28.50,
                'stock': 65,
                'description': 'Modul buck profesional cu TI TPS5430 pentru aplicatii care necesita ripple redus si zgomot minim. Frecventa fixa de comutare 500kHz pentru filtrare optima. Ideal pentru proiecte audio si sensibile EMC.',
                'platforms': ['arduino-uno', 'esp32', 'stm32'],
                'attrs': {
                    'input_range': (5.5, 36),
                    'output_voltage': 5.0,
                    'max_current': 3.0,
                    'converter_type': 'Buck',
                    'efficiency': 95.0,
                    'supply_voltage': 12.0,
                }
            },
            {
                'name': 'Pololu 5V 5A step-up/down S18V20F5',
                'slug': 'pololu-s18v20f5-buck-boost',
                'sku': 'DCC-00008',
                'manufacturer': 'Pololu',
                'price': 195.00,
                'stock': 22,
                'description': 'Convertor profesional buck-boost cu iesire fixa 5V si curent maxim 5A. Functioneaza atat la tensiuni de intrare mai mari cat si mai mici decat 5V. Folosit in proiecte de robotica unde tensiunea bateriei variaza mult.',
                'platforms': ['arduino-uno', 'arduino-mega', 'esp32', 'raspberry-pi'],
                'attrs': {
                    'input_range': (2.9, 32),
                    'output_voltage': 5.0,
                    'max_current': 5.0,
                    'converter_type': 'Buck-Boost',
                    'efficiency': 95.0,
                    'supply_voltage': 12.0,
                }
            },
        ]
        for d in products:
            self._make_product(cat, d, p)
