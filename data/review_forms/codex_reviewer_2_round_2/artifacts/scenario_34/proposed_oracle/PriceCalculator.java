public class PriceCalculator {
    private static final double MAX_DISCOUNT = 100.0;
    
    public double calculateDiscount(double price, String customerType) {
        double discount;
        if (customerType.equals("PREMIUM")) {
            if (price > 1000) {
                discount = price * 0.3;
            } else if (price > 500) {
                discount = price * 0.25;
            } else {
                discount = price * 0.2;
            }
        } else {
            discount = price * 0.1;
        }
        return Math.min(discount, MAX_DISCOUNT);
    }
}
