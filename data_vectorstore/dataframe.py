import pandas as pd
from sqlalchemy import create_engine

# SQLAlchemy를 사용한 MySQL 연결
engine = create_engine('mysql+pymysql://teamuser:StM!chel1905@3.34.46.30/dev_db')

# 매장별, 아이템별 판매량 (날짜 포함)
query_sales = """
SELECT 
    o.store, 
    i.item_id, 
    i.item_name, 
    DATE(o.order_at) AS order_date, 
    SUM(oi.item_count) AS total_sold,
    SUM(oi.item_count * i.sale_price) AS total_amount  -- 총 금액 추가
FROM kiosk_orderitem oi
JOIN kiosk_orderinfo o ON oi.order_id = o.order_id
JOIN menu_item i ON oi.item_id = i.item_id
GROUP BY o.store, i.item_id, i.item_name, order_date
ORDER BY o.store, order_date DESC, total_sold DESC;
"""
df_sales = pd.read_sql(query_sales, engine)

# 회원별 구매 패턴 분석 (선호 제품 3개 포함)
query_members = """
WITH FavoriteProducts AS (
    SELECT 
        m.member_id,
        m.name AS member_name,
        i.item_name,
        COUNT(*) AS product_count,
        RANK() OVER (PARTITION BY m.member_id ORDER BY COUNT(*) DESC) AS product_rank
    FROM kiosk_orderinfo o
    JOIN kiosk_paymentinfo p ON o.order_id = p.order_id
    JOIN member_member m ON p.member_id = m.member_id
    JOIN kiosk_orderitem oi ON o.order_id = oi.order_id
    JOIN menu_item i ON oi.item_id = i.item_id
    GROUP BY m.member_id, i.item_name
)
SELECT 
    m.member_id, 
    m.name AS member_name, 
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.final_amount) AS total_spent,
    GROUP_CONCAT(DISTINCT fp.item_name ORDER BY fp.product_rank SEPARATOR ', ') AS favorite_products  -- 중복 제거 및 정렬
FROM member_member m
LEFT JOIN kiosk_paymentinfo p ON m.member_id = p.member_id
LEFT JOIN kiosk_orderinfo o ON p.order_id = o.order_id
LEFT JOIN FavoriteProducts fp ON m.member_id = fp.member_id AND fp.product_rank <= 3
GROUP BY m.member_id, m.name
ORDER BY total_spent DESC;
"""
df_members = pd.read_sql(query_members, engine)

# 주문 상세 정보 (order_info + member 포함)
query_orders = """
SELECT 
    o.order_id,
    o.store,
    o.order_at,
    m.member_id,
    m.name AS member_name,
    o.final_amount,
    p.payment_method AS payment_type,
    i.item_id,
    i.item_name,
    oi.item_count
FROM kiosk_orderinfo o
LEFT JOIN kiosk_paymentinfo p ON o.order_id = p.order_id
LEFT JOIN member_member m ON p.member_id = m.member_id
LEFT JOIN kiosk_orderitem oi ON o.order_id = oi.order_id
LEFT JOIN menu_item i ON oi.item_id = i.item_id
ORDER BY o.order_at DESC;
"""
df_orders = pd.read_sql(query_orders, engine)

# 자주 묻는 질문 분석
query_qna = """
SELECT 
    q.qna_id, 
    q.title AS question_title, 
    q.content AS question_content, 
    r.content AS answer, 
    q.created_at AS question_date, 
    r.created_at AS answer_date
FROM member_qna q
LEFT JOIN member_qnareply r ON q.qna_id = r.qna_id
ORDER BY q.created_at DESC
LIMIT 10;
"""
df_qna = pd.read_sql(query_qna, engine)

# DB 연결 종료
engine.dispose()

# 데이터 확인
print(df_sales.head())
print(df_members.head())
print(df_orders.head())
print(df_qna.head())

# CSV로 내보내기
# df_sales.to_csv('sales_data.csv', index=False, encoding='utf-8-sig')
# df_members.to_csv('members_data.csv', index=False, encoding='utf-8-sig')
# df_orders.to_csv('orders_data.csv', index=False, encoding='utf-8-sig')
# df_qna.to_csv('qna_data.csv', index=False, encoding='utf-8-sig')
