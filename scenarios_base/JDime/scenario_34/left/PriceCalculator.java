public class PriceCalculator {
    public double calculateDiscount(double price, String customerType) {
        if (customerType.equals("PREMIUM")) {
            if (price > 1000) return price * 0.3;
            if (price > 500) return price * 0.25;
            return price * 0.2;
        }
        return price * 0.1;
    }
}