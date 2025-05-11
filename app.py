from flask import Flask, request, jsonify
import pandas as pd
import ast

app = Flask(__name__)
# 全局加载数据
df = pd.read_csv('product_info.csv')

@app.route('/products', methods=['POST'])
def get_products():
    data = request.get_json()
    skin = data.get('skin_type', '').lower()
    if not skin:
        return jsonify({'error': '缺少 skin_type 参数'}), 400

    # 根据 skin_type 过滤 highlights 或 product_name（忽略大小写）
    mask = df['highlights'].str.contains(skin, case=False, na=False) |            df['product_name'].str.contains(skin, case=False, na=False)
    filtered = df[mask]

    result = []
    for _, row in filtered.iterrows():
        name = row['product_name']
        price = row['price_usd']
        
        # 解析成分列表并取前5个
        raw_ing = row['ingredients']
        try:
            ing_list = ast.literal_eval(raw_ing)
        except Exception:
            ing_list = [raw_ing]
        if len(ing_list) == 1:
            # 单元素列表，按逗号拆分
            parts = ing_list[0].split(',')
            ing_items = [ing.strip() for ing in parts if ing.strip()]
        else:
            ing_items = []
            for part in ing_list:
                parts = part.split(',')
                ing_items += [ing.strip() for ing in parts if ing.strip()]
        first_five = ing_items[:5]

        result.append({
            'name': name,
            'price': price,
            'ingredients': first_five,
            'comments': None     # 当前无评论数据，返回 null
        })

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
