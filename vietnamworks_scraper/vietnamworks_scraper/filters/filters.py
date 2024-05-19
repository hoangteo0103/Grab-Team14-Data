from enum import Enum

class CityFilter(Enum):
    INTERNATIONAL = "70"
    HA_NOI = "24"
    HO_CHI_MINH = "29"
    HAI_PHONG = "28"
    DA_NANG = "17"
    CAN_THO = "15"
    BA_RIA_VUNG_TAU = "3"
    AN_GIANG = "2"
    BAC_GIANG = "5"
    BAC_KAN = "4"
    BAC_LIEU = "6"
    BAC_NINH = "7"
    BEN_TRE = "8"
    BINH_DINH = "10"
    BINH_DUONG = "11"
    BINH_PHUOC = "12"
    BINH_THUAN = "13"
    CA_MAU = "14"
    CAO_BANG = "16"
    DAK_LAK = "18"
    DAK_NONG = "73"
    MEKONG_DELTA = "71"
    DIEN_BIEN = "69"
    DONG_NAI = "19"
    DONG_THAP = "20"
    GIA_LAI = "21"
    HA_GIANG = "22"
    HA_NAM = "23"
    HA_TINH = "26"
    HAI_DUONG = "27"
    HAU_GIANG = "72"
    HOA_BINH = "30"
    HUNG_YEN = "32"
    KHANH_HOA = "33"
    KIEN_GIANG = "61"
    KON_TUM = "34"
    LAI_CHAU = "35"
    LAM_DONG = "36"
    LANG_SON = "37"
    LAO_CAI = "38"
    LONG_AN = "39"
    NAM_DINH = "40"
    NGHE_AN = "41"
    NINH_BINH = "42"
    NINH_THUAN = "43"
    PHU_THO = "44"
    PHU_YEN = "45"
    QUANG_BINH = "46"
    QUANG_NAM = "47"
    QUANG_NGAI = "48"
    QUANG_NINH = "49"
    QUANG_TRI = "50"
    SOC_TRANG = "51"
    SON_LA = "52"
    TAY_NINH = "53"
    THAI_BINH = "54"
    THAI_NGUYEN = "55"
    THANH_HOA = "56"
    THUA_THIEN_HUE = "57"
    TIEN_GIANG = "58"
    TRA_VINH = "59"
    TUYEN_QUANG = "60"
    VINH_LONG = "62"
    VINH_PHUC = "63"
    YEN_BAI = "65"
    OTHER = "66"

class TypeFilters(Enum):
    FULL_TIME = "1"
    PART_TIME = "2"
    INTERNSHIP = "3"
    TEMPORARY = "5"
    CONTRACT = "1"
    VOLUNTEER = "4"
    OTHER = "6"
    ANY = "0"
    

class ExperienceLevelFilters(Enum):
    INTERNSHIP = "8"
    ENTRY_LEVEL = "1"
    ASSOCIATE = "5"
    MID_SENIOR = "7"
    DIRECTOR = "3"
    EXECUTIVE = "3"
    ANY = "0"
    def __init__(self, value):
        super().__init__(value)


class IndustryFilter(Enum):
    def __init__(self, value):
        super().__init__(value)
    

        RETAIL_CONSUMER_PRODUCTS = 24
    # INSURANCE = 14
    # REAL_ESTATE = 23
    # CEO_GENERAL_MANAGEMENT = 29
    # GOVERNMENT_NGO = 25
    # IT_TELECOMMUNICATIONS = 5
    # PHARMACY = 28
    # TEXTILES_GARMENTS_FOOTWEAR = 26
    # CUSTOMER_SERVICE = 6
    # FOOD_BEVERAGE = 11
    # EDUCATION = 1
    # ADMIN_OFFICE_SUPPORT = 20
    # LOGISTICS_IMPORT_EXPORT_WAREHOUSE = 13
    # ENGINEERING_SCIENCES = 9
    # SALES = 21
    # ARCHITECTURE_CONSTRUCTION = 4
    # ACCOUNTING_AUDITING = 2
    # TECHNICIAN = 22
    # ART_MEDIA_PRINTING_PUBLISHING = 18
    # BANKING_FINANCIAL_SERVICES = 10
    # HOSPITALITY_TOURISM = 15
    # HR_RECRUITMENT = 12
    # AGRICULTURE_LIVESTOCK_FISHERY = 3
    # LEGAL = 16
    # MANUFACTURING = 27
    # DESIGN = 7
    # MARKETING_ADVERTISING_COMMUNICATIONS = 17
    # TRANSPORTATION = 8
    # HEALTHCARE_MEDICAL_SERVICES = 19
    # OTHERS = 30

    ACCOMMODATION_SERVICES = "15"
    ADMINISTRATIVE_AND_SUPPORT_SERVICES = "20"
    CONSTRUCTION = "4"
    CONSUMER_SERVICES = "6"
    EDUCATION = "1"
    ENTERTAINMENT_PROVIDERS = "18"
    FARMING_RANCHING_FORESTRY = "3"
    FINANCIAL_SERVICES = "10"
    GOVERNMENT_ADMINISTRATION = "25"
    HOSPITALS_AND_HEALTH_CARE = "19"
    MANUFACTURING = "27"
    REAL_ESTATE_AND_EQUIPMENT_RENTAL_SERVICES = "23"
    RETAIL = "24"
    TECHNOLOGY_INFORMATION_AND_MEDIA = "5.9.22"
