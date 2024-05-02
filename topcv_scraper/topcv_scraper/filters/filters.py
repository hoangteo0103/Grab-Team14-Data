from enum import Enum

class CityFilter(Enum):
    Ha_Noi = "1"
    Ho_Chi_Minh = "2"
    Binh_Duong = "3"
    Bac_Ninh = "4"
    Dong_Nai = "5"
    Hung_Yen = "6"
    Hai_Duong = "7"
    Da_Nang = "8"
    Hai_Phong = "9"
    An_Giang = "10"
    Ba_Ria_Vung_Tau = "11"
    Bac_Giang = "12"
    Bac_Kan = "13"
    Bac_Lieu = "14"
    Ben_Tre = "15"
    Binh_Dinh = "16"
    Binh_Phuoc = "17"
    Binh_Thuan = "18"
    Ca_Mau = "19"
    Can_Tho = "20"
    Cao_Bang = "21"
    Cuu_Long = "22"
    Dak_Lak = "23"
    Dak_Nong = "24"
    Dien_Bien = "25"
    Dong_Thap = "26"
    Gia_Lai = "27"
    Ha_Giang = "28"
    Ha_Nam = "29"
    Ha_Tinh = "30"
    Hau_Giang = "31"
    Hoa_Binh = "32"
    Khanh_Hoa = "33"
    Kien_Giang = "34"
    Kon_Tum = "35"
    Lai_Chau = "36"
    Lam_Dong = "37"
    Lang_Son = "38"
    Lao_Cai = "39"
    Long_An = "40"
    Mien_Bac = "41"
    Mien_Nam = "42"
    Mien_Trung = "43"
    Nam_Dinh = "44"
    Nghe_An = "45"
    Ninh_Binh = "46"
    Ninh_Thuan = "47"
    Phu_Tho = "48"
    Phu_Yen = "49"
    Quang_Binh = "50"
    Quang_Nam = "51"
    Quang_Ngai = "52"
    Quang_Ninh = "53"
    Quang_Tri = "54"
    Soc_Trang = "55"
    Son_La = "56"
    Tay_Ninh = "57"
    Thai_Binh = "58"
    Thai_Nguyen = "59"
    Thanh_Hoa = "60"
    Thua_Thien_Hue = "61"
    Tien_Giang = "62"
    Toan_Quoc = "63"
    Tra_Vinh = "64"
    Tuyen_Quang = "65"
    Vinh_Long = "66"
    Vinh_Phuc = "67"
    Yen_Bai = "68"
    Nuoc_Ngoai = "100"
    @staticmethod
    def getValueFromKey(key):
        key = key.replace(" ", "_")
        for k, v in CityFilter.__members__.items():
            if v.name == key:
                return v.value

class JobTypeFilter(Enum):
    FULL_TIME = "1"
    PART_TIME = "3"
    INTERNSHIP = "5"
    def __str__(self):
        return self.name 
    def getValueFromKey(key):
        for k, v in JobTypeFilter.__members__.items():
            if v.name == key:
                return v.value

class IndustryFilter(Enum):
    # All_Industries = None
    # Agency_Design_Development = "33"
    # Agency_Marketing_Advertising = "34"
    # Retail_Consumer_Goods_FMCG = "11"
    # Insurance = "4"
    # Maintenance_Repair = "20"
    # Real_Estate = "5"
    # Securities = "13"
    # Mechanical = "23"
    # Government_Agency = "30"
    # Tourism = "31"
    # Pharmaceuticals_Healthcare_Biotechnology = "6"
    # Electronics_Refrigeration = "21"
    # Entertainment = "36"
    # Education_Training = "26"
    # Printing_Publishing = "10"
    # Internet_Online = "7"
    # IT_Hardware = "37"
    # IT_Software = "1"
    # Accounting_Auditing = "2"
    # Other = "10000"
    # Logistics_Transportation = "28"
    # Law = "3"
    # Marketing_Communications_Advertising = "8"
    # Environment = "18"
    # Energy = "35"
    # Banking = "15"
    # Restaurant_Hotel = "9"
    # Human_Resources = "16"
    # Agriculture_Forestry_Fisheries = "38"
    # Manufacturing = "12"
    # Finance = "39"
    # Design_Architecture = "17"
    # Fashion = "22"
    # Ecommerce = "27"
    # Non_Profit_Organization = "29"
    # Automation = "32"
    # Consultancy = "24"
    # Telecommunications = "25"
    # Construction = "14"
    # Import_Export = "19"

    # Mapping to linkedin
    ACCOMMODATION_SERVICES = "9"
    ADMINISTRATIVE_AND_SUPPOR_SERVICES = "33.3"
    CONSTRUCTION = "14"
    CONSUMER_SERVICES = "27"
    EDUCATION = "26"
    ENTERTAINMENT_PROVIDERS = "36"
    FARMING_RANCHING_FORESTRY = "38"
    FINANCIAL_SERVICES = "39"
    GOVERNMENT_ADMINISTRATION = "30"
    HOSPITALS_AND_HEALTH_CARE = "6"
    MANUFACTURING = "12"
    PROFESSIONAL_SERVICES = "8"
    REAL_ESTATE_AND_EQUIPMENT_RENTAL_SERVICES = "5"
    RETAIL = "11"
    TECHNOLOGY_INFORMATION_AND_MEDIA = "1.7.37"


    
    @staticmethod
    def getValueFromKey(key):
        key = key.replace(" ", "_")
        for k, v in IndustryFilter.__members__.items():
            if v.name == key:
                return v.value