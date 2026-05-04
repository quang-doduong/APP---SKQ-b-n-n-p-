# logic_module.py
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import datetime
from geopy.geocoders import Nominatim
import osmnx as ox
import networkx as nx

# --- HỆ THỐNG LOGIC MỜ 27 RULES ---
mat_do = ctrl.Antecedent(np.arange(0, 11, 1), 'mat_do')           
loai_xe = ctrl.Antecedent(np.arange(1, 4, 1), 'loai_xe')          
thoi_gian_doi = ctrl.Antecedent(np.arange(1, 4, 1), 'thoi_gian_doi') 
he_so_x = ctrl.Consequent(np.arange(1.0, 3.1, 0.1), 'he_so_x')

mat_do.automf(3, names=['vang', 'vua', 'dong'])
loai_xe.automf(3, names=['hai_banh', 'taxi_4', 'taxi_7'])
thoi_gian_doi.automf(3, names=['lau', 'binh_thuong', 'gap'])

he_so_x['thap'] = fuzz.trimf(he_so_x.universe, [1.0, 1.0, 1.5])
he_so_x['vua'] = fuzz.trimf(he_so_x.universe, [1.3, 1.8, 2.3])
he_so_x['cao'] = fuzz.trimf(he_so_x.universe, [2.0, 3.0, 3.0])

# --- ĐỊNH NGHĨA 27 RULES ---
# Nhóm 1: Đường vắng
r1 = ctrl.Rule(mat_do['vang'] & loai_xe['hai_banh'] & thoi_gian_doi['lau'], he_so_x['thap'])
r2 = ctrl.Rule(mat_do['vang'] & loai_xe['hai_banh'] & thoi_gian_doi['binh_thuong'], he_so_x['thap'])
r3 = ctrl.Rule(mat_do['vang'] & loai_xe['hai_banh'] & thoi_gian_doi['gap'], he_so_x['vua'])
r4 = ctrl.Rule(mat_do['vang'] & loai_xe['taxi_4'] & thoi_gian_doi['lau'], he_so_x['thap'])
r5 = ctrl.Rule(mat_do['vang'] & loai_xe['taxi_4'] & thoi_gian_doi['binh_thuong'], he_so_x['vua'])
r6 = ctrl.Rule(mat_do['vang'] & loai_xe['taxi_4'] & thoi_gian_doi['gap'], he_so_x['cao'])
r7 = ctrl.Rule(mat_do['vang'] & loai_xe['taxi_7'] & thoi_gian_doi['lau'], he_so_x['vua'])
r8 = ctrl.Rule(mat_do['vang'] & loai_xe['taxi_7'] & thoi_gian_doi['binh_thuong'], he_so_x['cao'])
r9 = ctrl.Rule(mat_do['vang'] & loai_xe['taxi_7'] & thoi_gian_doi['gap'], he_so_x['cao'])
# Nhóm 2: Đường vừa
r10 = ctrl.Rule(mat_do['vua'] & loai_xe['hai_banh'] & thoi_gian_doi['lau'], he_so_x['thap'])
r11 = ctrl.Rule(mat_do['vua'] & loai_xe['hai_banh'] & thoi_gian_doi['binh_thuong'], he_so_x['vua'])
r12 = ctrl.Rule(mat_do['vua'] & loai_xe['hai_banh'] & thoi_gian_doi['gap'], he_so_x['cao'])
r13 = ctrl.Rule(mat_do['vua'] & loai_xe['taxi_4'] & thoi_gian_doi['lau'], he_so_x['vua'])
r14 = ctrl.Rule(mat_do['vua'] & loai_xe['taxi_4'] & thoi_gian_doi['binh_thuong'], he_so_x['vua'])
r15 = ctrl.Rule(mat_do['vua'] & loai_xe['taxi_4'] & thoi_gian_doi['gap'], he_so_x['cao'])
r16 = ctrl.Rule(mat_do['vua'] & loai_xe['taxi_7'] & thoi_gian_doi['lau'], he_so_x['cao'])
r17 = ctrl.Rule(mat_do['vua'] & loai_xe['taxi_7'] & thoi_gian_doi['binh_thuong'], he_so_x['cao'])
r18 = ctrl.Rule(mat_do['vua'] & loai_xe['taxi_7'] & thoi_gian_doi['gap'], he_so_x['cao'])
# Nhóm 3: Đường đông
r19 = ctrl.Rule(mat_do['dong'] & loai_xe['hai_banh'] & thoi_gian_doi['lau'], he_so_x['vua'])
r20 = ctrl.Rule(mat_do['dong'] & loai_xe['hai_banh'] & thoi_gian_doi['binh_thuong'], he_so_x['cao'])
r21 = ctrl.Rule(mat_do['dong'] & loai_xe['hai_banh'] & thoi_gian_doi['gap'], he_so_x['cao'])
r22 = ctrl.Rule(mat_do['dong'] & loai_xe['taxi_4'] & thoi_gian_doi['lau'], he_so_x['cao'])
r23 = ctrl.Rule(mat_do['dong'] & loai_xe['taxi_4'] & thoi_gian_doi['binh_thuong'], he_so_x['cao'])
r24 = ctrl.Rule(mat_do['dong'] & loai_xe['taxi_4'] & thoi_gian_doi['gap'], he_so_x['cao'])
r25 = ctrl.Rule(mat_do['dong'] & loai_xe['taxi_7'] & thoi_gian_doi['lau'], he_so_x['cao'])
r26 = ctrl.Rule(mat_do['dong'] & loai_xe['taxi_7'] & thoi_gian_doi['binh_thuong'], he_so_x['cao'])
r27 = ctrl.Rule(mat_do['dong'] & loai_xe['taxi_7'] & thoi_gian_doi['gap'], he_so_x['cao'])

tinh_gia_logic = ctrl.ControlSystem([r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12,r13,r14,r15,r16,r17,r18,r19,r20,r21,r22,r23,r24,r25,r26,r27])
app_tinh_phi = ctrl.ControlSystemSimulation(tinh_gia_logic)

def calculate_trip(A, B, xe_val, doi_val):
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
    app_tinh_phi.compute()
    X = app_tinh_phi.output['he_so_x']

    geolocator = Nominatim(user_agent="taxi_app_final")
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
    price = km * 10000 * X

    return tinh_trang, km, X, price, (loc_A.latitude, loc_A.longitude), (loc_B.latitude, loc_B.longitude), coords, midpoint