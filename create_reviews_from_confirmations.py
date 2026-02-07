from app import app, db, DeliveryConfirmation, Review, Order
import json

with app.app_context():
    # Get all delivery confirmations that don't have reviews yet
    confirmations = DeliveryConfirmation.query.all()
    
    reviews_created = 0
    
    for confirmation in confirmations:
        order = Order.query.get(confirmation.order_id)
        if not order or not order.items:
            continue
        
        try:
            items = json.loads(order.items)
            for item in items:
                product_id = item.get('id')
                if product_id:
                    # Check if review already exists
                    existing = Review.query.filter_by(
                        product_id=product_id, 
                        user_id=confirmation.user_id
                    ).first()
                    
                    if not existing:
                        review = Review(
                            product_id=product_id,
                            user_id=confirmation.user_id,
                            rating=confirmation.rating,
                            comment=confirmation.feedback,
                            created_at=confirmation.created_at
                        )
                        db.session.add(review)
                        reviews_created += 1
                        print(f"Created review for product {product_id} from order {order.id}")
        except Exception as e:
            print(f"Error processing order {order.id}: {e}")
    
    db.session.commit()
    print(f"\nCreated {reviews_created} reviews from existing delivery confirmations!")
