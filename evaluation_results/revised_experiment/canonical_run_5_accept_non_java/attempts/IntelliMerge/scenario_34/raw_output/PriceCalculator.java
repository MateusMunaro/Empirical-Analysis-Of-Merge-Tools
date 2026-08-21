public class PriceCalculator {
    private static final double MAX_DISCOUNT = 100.0;
    
    public double calculateDiscount(double price, String customerType) {
        double discount;
        if (customerType.equals("PREMIUM")) {
<<<<<<< ours
            if (price > 1000) return price * 0.3;
            if (price > 500) return price * 0.25;
            return price * 0.2;
=======
            discount = price * 0.2;
        } else {
            discount = price * 0.1;
>>>>>>> theirs
        }
        return Math.min(discount, MAX_DISCOUNT);
    }
}