import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import datetime
from geopy.geocoders import Nominatim
import osmnx as ox
import networkx as nx

# --- 1. KHAI BÁO THÊM BIẾN QUÃNG ĐƯỜNG ---
mat_do = ctrl.Antecedent(np.arange(0, 11, 1), 'mat_do')           
loai_xe = ctrl.Antecedent(np.arange(1, 4, 1), 'loai_xe')          
thoi_gian_doi = ctrl.Antecedent(np.arange(1, 4, 1), 'thoi_gian_doi') 
quang_duong = ctrl.Antecedent(np.arange(0, 101, 1), 'quang_duong') # Thêm biến quãng đường (0-100km)
he_so_x = ctrl.Consequent(np.arange(1.0, 3.1, 0.1), 'he_so_x')

mat_do.automf(3, names=['vang', 'vua', 'dong'])
loai_xe.automf(3, names=['hai_banh', 'taxi_4', 'taxi_7'])
thoi_gian_doi.automf(3, names=['lau', 'binh_thuong', 'gap'])

# Định nghĩa tập mờ cho Quãng đường
quang_duong['ngan'] = fuzz.trimf(quang_duong.universe, [0, 0, 5])
quang_duong['vua'] = fuzz.trimf(quang_duong.universe, [3, 10, 20])
quang_duong['dai'] = fuzz.trimf(quang_duong.universe, [15, 100, 100])

he_so_x['thap'] = fuzz.trimf(he_so_x.universe, [1.0, 1.0, 1.5])
he_so_x['vua'] = fuzz.trimf(he_so_x.universe, [1.3, 1.8, 2.3])
he_so_x['cao'] = fuzz.trimf(he_so_x.universe, [2.0, 3.0, 3.0])



#Toàn bộ 81 luật được tạo ở đây
# 27 luật cho đường vắng
rules_vang = [
    # Xe 2 bánh (9 luật)
    ctrl.Rule(mat_do['vang'] & loai_xe['hai_banh'] & thoi_gian_doi['lau'] & quang_duong['ngan'], he_so_x['thap']),
    ctrl.Rule(mat_do['vang'] & loai_xe['hai_banh'] & thoi_gian_doi['lau'] & quang_duong['vua'], he_so_x['thap']),
    ctrl.Rule(mat_do['vang'] & loai_xe['hai_banh'] & thoi_gian_doi['lau'] & quang_duong['dai'], he_so_x['thap']),
    ctrl.Rule(mat_do['vang'] & loai_xe['hai_banh'] & thoi_gian_doi['binh_thuong'] & quang_duong['ngan'], he_so_x['thap']),
    ctrl.Rule(mat_do['vang'] & loai_xe['hai_banh'] & thoi_gian_doi['binh_thuong'] & quang_duong['vua'], he_so_x['vua']),
    ctrl.Rule(mat_do['vang'] & loai_xe['hai_banh'] & thoi_gian_doi['binh_thuong'] & quang_duong['dai'], he_so_x['vua']),
    ctrl.Rule(mat_do['vang'] & loai_xe['hai_banh'] & thoi_gian_doi['gap'] & quang_duong['ngan'], he_so_x['vua']),
    ctrl.Rule(mat_do['vang'] & loai_xe['hai_banh'] & thoi_gian_doi['gap'] & quang_duong['vua'], he_so_x['vua']),
    ctrl.Rule(mat_do['vang'] & loai_xe['hai_banh'] & thoi_gian_doi['gap'] & quang_duong['dai'], he_so_x['cao']),

    # Taxi 4 chỗ (9 luật)
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_4'] & thoi_gian_doi['lau'] & quang_duong['ngan'], he_so_x['thap']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_4'] & thoi_gian_doi['lau'] & quang_duong['vua'], he_so_x['thap']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_4'] & thoi_gian_doi['lau'] & quang_duong['dai'], he_so_x['vua']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_4'] & thoi_gian_doi['binh_thuong'] & quang_duong['ngan'], he_so_x['vua']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_4'] & thoi_gian_doi['binh_thuong'] & quang_duong['vua'], he_so_x['vua']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_4'] & thoi_gian_doi['binh_thuong'] & quang_duong['dai'], he_so_x['cao']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_4'] & thoi_gian_doi['gap'] & quang_duong['ngan'], he_so_x['cao']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_4'] & thoi_gian_doi['gap'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_4'] & thoi_gian_doi['gap'] & quang_duong['dai'], he_so_x['cao']),

    # Taxi 7 chỗ (9 luật)
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_7'] & thoi_gian_doi['lau'] & quang_duong['ngan'], he_so_x['vua']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_7'] & thoi_gian_doi['lau'] & quang_duong['vua'], he_so_x['vua']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_7'] & thoi_gian_doi['lau'] & quang_duong['dai'], he_so_x['cao']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_7'] & thoi_gian_doi['binh_thuong'] & quang_duong['ngan'], he_so_x['cao']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_7'] & thoi_gian_doi['binh_thuong'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_7'] & thoi_gian_doi['binh_thuong'] & quang_duong['dai'], he_so_x['cao']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_7'] & thoi_gian_doi['gap'] & quang_duong['ngan'], he_so_x['cao']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_7'] & thoi_gian_doi['gap'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['vang'] & loai_xe['taxi_7'] & thoi_gian_doi['gap'] & quang_duong['dai'], he_so_x['cao']),
]

# 27 luật cho đường mật độ trung bình
rules_vua = [
    # Xe 2 bánh (9 luật)
    ctrl.Rule(mat_do['vua'] & loai_xe['hai_banh'] & thoi_gian_doi['lau'] & quang_duong['ngan'], he_so_x['thap']),
    ctrl.Rule(mat_do['vua'] & loai_xe['hai_banh'] & thoi_gian_doi['lau'] & quang_duong['vua'], he_so_x['vua']),
    ctrl.Rule(mat_do['vua'] & loai_xe['hai_banh'] & thoi_gian_doi['lau'] & quang_duong['dai'], he_so_x['vua']),
    ctrl.Rule(mat_do['vua'] & loai_xe['hai_banh'] & thoi_gian_doi['binh_thuong'] & quang_duong['ngan'], he_so_x['vua']),
    ctrl.Rule(mat_do['vua'] & loai_xe['hai_banh'] & thoi_gian_doi['binh_thuong'] & quang_duong['vua'], he_so_x['vua']),
    ctrl.Rule(mat_do['vua'] & loai_xe['hai_banh'] & thoi_gian_doi['binh_thuong'] & quang_duong['dai'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['hai_banh'] & thoi_gian_doi['gap'] & quang_duong['ngan'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['hai_banh'] & thoi_gian_doi['gap'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['hai_banh'] & thoi_gian_doi['gap'] & quang_duong['dai'], he_so_x['cao']),

    # Taxi 4 chỗ (9 luật)
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_4'] & thoi_gian_doi['lau'] & quang_duong['ngan'], he_so_x['vua']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_4'] & thoi_gian_doi['lau'] & quang_duong['vua'], he_so_x['vua']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_4'] & thoi_gian_doi['lau'] & quang_duong['dai'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_4'] & thoi_gian_doi['binh_thuong'] & quang_duong['ngan'], he_so_x['vua']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_4'] & thoi_gian_doi['binh_thuong'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_4'] & thoi_gian_doi['binh_thuong'] & quang_duong['dai'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_4'] & thoi_gian_doi['gap'] & quang_duong['ngan'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_4'] & thoi_gian_doi['gap'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_4'] & thoi_gian_doi['gap'] & quang_duong['dai'], he_so_x['cao']),

    # Taxi 7 chỗ (9 luật)
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_7'] & thoi_gian_doi['lau'] & quang_duong['ngan'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_7'] & thoi_gian_doi['lau'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_7'] & thoi_gian_doi['lau'] & quang_duong['dai'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_7'] & thoi_gian_doi['binh_thuong'] & quang_duong['ngan'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_7'] & thoi_gian_doi['binh_thuong'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_7'] & thoi_gian_doi['binh_thuong'] & quang_duong['dai'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_7'] & thoi_gian_doi['gap'] & quang_duong['ngan'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_7'] & thoi_gian_doi['gap'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['vua'] & loai_xe['taxi_7'] & thoi_gian_doi['gap'] & quang_duong['dai'], he_so_x['cao']),
]
# 27 luật cho đường đông đúc 
rules_dong = [
    # --- XE HAI BÁNH (9 luật) ---
    ctrl.Rule(mat_do['dong'] & loai_xe['hai_banh'] & thoi_gian_doi['lau'] & quang_duong['ngan'], he_so_x['thap']),
    ctrl.Rule(mat_do['dong'] & loai_xe['hai_banh'] & thoi_gian_doi['lau'] & quang_duong['vua'], he_so_x['vua']),
    ctrl.Rule(mat_do['dong'] & loai_xe['hai_banh'] & thoi_gian_doi['lau'] & quang_duong['dai'], he_so_x['vua']),
    ctrl.Rule(mat_do['dong'] & loai_xe['hai_banh'] & thoi_gian_doi['binh_thuong'] & quang_duong['ngan'], he_so_x['vua']),
    ctrl.Rule(mat_do['dong'] & loai_xe['hai_banh'] & thoi_gian_doi['binh_thuong'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['hai_banh'] & thoi_gian_doi['binh_thuong'] & quang_duong['dai'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['hai_banh'] & thoi_gian_doi['gap'] & quang_duong['ngan'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['hai_banh'] & thoi_gian_doi['gap'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['hai_banh'] & thoi_gian_doi['gap'] & quang_duong['dai'], he_so_x['cao']),

    # --- TAXI 4 CHỖ (9 luật) ---
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_4'] & thoi_gian_doi['lau'] & quang_duong['ngan'], he_so_x['vua']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_4'] & thoi_gian_doi['lau'] & quang_duong['vua'], he_so_x['vua']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_4'] & thoi_gian_doi['lau'] & quang_duong['dai'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_4'] & thoi_gian_doi['binh_thuong'] & quang_duong['ngan'], he_so_x['vua']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_4'] & thoi_gian_doi['binh_thuong'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_4'] & thoi_gian_doi['binh_thuong'] & quang_duong['dai'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_4'] & thoi_gian_doi['gap'] & quang_duong['ngan'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_4'] & thoi_gian_doi['gap'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_4'] & thoi_gian_doi['gap'] & quang_duong['dai'], he_so_x['cao']),

    # --- TAXI 7 CHỖ (9 luật) ---
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_7'] & thoi_gian_doi['lau'] & quang_duong['ngan'], he_so_x['vua']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_7'] & thoi_gian_doi['lau'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_7'] & thoi_gian_doi['lau'] & quang_duong['dai'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_7'] & thoi_gian_doi['binh_thuong'] & quang_duong['ngan'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_7'] & thoi_gian_doi['binh_thuong'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_7'] & thoi_gian_doi['binh_thuong'] & quang_duong['dai'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_7'] & thoi_gian_doi['gap'] & quang_duong['ngan'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_7'] & thoi_gian_doi['gap'] & quang_duong['vua'], he_so_x['cao']),
    ctrl.Rule(mat_do['dong'] & loai_xe['taxi_7'] & thoi_gian_doi['gap'] & quang_duong['dai'], he_so_x['cao']),
]


# gộp tất cả lại 
all_rules = rules_vang + rules_vua + rules_dong
tinh_gia_logic = ctrl.ControlSystem(all_rules)
app_tinh_phi = ctrl.ControlSystemSimulation(tinh_gia_logic)



def calculate_trip(A, B, xe_val, doi_val):
    # 1. Geocode và tính Quãng đường TRƯỚC
    # geolocator = Nominatim(user_agent="taxi_app_final")
    geolocator = Nominatim(user_agent="my_unique_taxi_app_2024", timeout=10)
    loc_A = geolocator.geocode(A)
    loc_B = geolocator.geocode(B)
    if not loc_A or not loc_B:
        raise ValueError("Không tìm thấy địa chỉ. Hãy thử ghi rõ Tên Đường, Quận, Thành phố.")

    midpoint = ((loc_A.latitude + loc_B.latitude) / 2, (loc_A.longitude + loc_B.longitude) / 2)
    G = ox.graph_from_point(midpoint, dist=5000, network_type='drive') 
    orig = ox.distance.nearest_nodes(G, loc_A.longitude, loc_A.latitude)
    dest = ox.distance.nearest_nodes(G, loc_B.longitude, loc_B.latitude)
    
    route = nx.shortest_path(G, orig, dest, weight="length")
    coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]
    km = nx.path_weight(G, route, weight='length') / 1000

    # 2. Đưa dữ liệu vào hệ thống mờ (bao gồm cả km vừa tính)
    now = datetime.datetime.now()
    current_hour = now.hour
    if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
        mat_do_thuc_te, tinh_trang = 9, f"{current_hour}h: Cao điểm"
    elif 22 <= current_hour or current_hour <= 6:
        mat_do_thuc_te, tinh_trang = 2, f"{current_hour}h: Đêm muộn"
    else:
        mat_do_thuc_te, tinh_trang = 5, f"{current_hour}h: Bình thường"

    app_tinh_phi.input['mat_do'] = mat_do_thuc_te
    app_tinh_phi.input['loai_xe'] = xe_val
    app_tinh_phi.input['thoi_gian_doi'] = doi_val
    app_tinh_phi.input['quang_duong'] = km # Truyền tham số thứ 4
    
    app_tinh_phi.compute()
    X = app_tinh_phi.output['he_so_x']

    # 3. Tính tiền
    price = km * 10000 * X

    return tinh_trang, km, X, price, (loc_A.latitude, loc_A.longitude), (loc_B.latitude, loc_B.longitude), coords, midpoint