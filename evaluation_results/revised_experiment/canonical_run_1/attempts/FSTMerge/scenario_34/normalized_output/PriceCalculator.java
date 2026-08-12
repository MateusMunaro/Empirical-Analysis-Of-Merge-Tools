public   class  PriceCalculator {
	
    
    public double calculateDiscount  (double price, String customerType) {
        double discount;
        if (customerType.equals("PREMIUM")) {
            discount = price * 0.2;
        } else {
            discount = price * 0.1;
        }
        return Math.min(discount, MAX_DISCOUNT);
    }

	
    private static final double MAX_DISCOUNT = 100.0;


}
