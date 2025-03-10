TABLE_SCHEMA = """
kiosk_orderinfo: order_id (PK), order_at(주문 일시: 날짜+시간), total_amount(주문 총액), store(A: 서초점 B: 강남점), earned_points(적립 포인트), final_amount(최종 결제 금액), total_count(합계 수량)
kiosk_orderitem: order_item_id (PK), order_id (FK to OrderInfo), item_id (FK to Item), item_count(주문 항목별 수량), item_total(주문 항목별 총액)
kiosk_paymentinfo: payment_id (PK), order_id (FK to OrderInfo), member_id (FK to Member, null: 비회원), payment_method(결제 수단, credit: 카드, epay: 간편결제), payment_status(결제 상태, 1: 결제 완료, 0: 결체 취소), pay_at(결제 일시: 날짜+시간), used_points(사용된 포인트)
member_member: member_id (PK), name, sex(M: 남성, F: 여성), age_group(연령대: 20, 30, 40, 50, 60), total_spent(총 소비 금액), points(보유 포인트), last_visited(마지막 방문일: 날짜+시간), visit_count(방문 횟수), member_type(회원 유형), store(A: 서초점 B: 강남점, membertype==manager인 경우만 존재), earning_rate(적립 비율, membertype==manager인 경우만 존재)
menu_item: item_id (PK), item_name(제품명), store(A: 서초점 B: 강남점), sale_price(판매가), cost_price(원가), category(dessert: 디저트류, bread: 빵류), stock(재고), created_at(제품 등록 일시: 날짜+시간), best(인기상품 여부, boolean type), new(신상품 여부, boolean type), show(홈페이지 노출 여부, boolean type)
menu_nutritioninfo: item_id (FK), nutrition_calories(칼로리)
"""