import pandas as pd
import numpy as np
from app import create_app
from app.models.entities import Order, Review, Complaint


app = create_app()


def build_operation_report(output_csv: str = "operation_report.csv"):
    with app.app_context():
        orders = Order.query.all()
        reviews = Review.query.all()
        complaints = Complaint.query.all()

        order_rows = [
            {
                "order_id": o.id,
                "status": o.status,
                "service_item_id": o.service_item_id,
                "created_at": o.created_at,
            }
            for o in orders
        ]
        review_rows = [{"order_id": r.order_id, "rating": r.rating} for r in reviews]

        df_orders = pd.DataFrame(order_rows)
        df_reviews = pd.DataFrame(review_rows)

        if df_orders.empty:
            print("暂无订单数据")
            return

        if not df_reviews.empty:
            merged = df_orders.merge(df_reviews, on="order_id", how="left")
        else:
            merged = df_orders.copy()
            merged["rating"] = np.nan

        summary = {
            "total_orders": len(df_orders),
            "completed_orders": int((df_orders["status"] == "completed").sum()),
            "completion_rate": float((df_orders["status"] == "completed").mean()),
            "avg_rating": float(np.nanmean(merged["rating"].values)) if merged["rating"].notna().any() else 0.0,
            "complaint_count": len(complaints),
        }

        out = pd.DataFrame([summary])
        out.to_csv(output_csv, index=False, encoding="utf-8-sig")
        print(f"运营报表已输出: {output_csv}")


if __name__ == "__main__":
    build_operation_report()
