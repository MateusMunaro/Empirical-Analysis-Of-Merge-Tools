public   class  Order {
	
    private int orderId  ;

	
    private double orderAmount;

	

    public Order  (int orderId, double orderAmount) {
        this.orderId = orderId;
        this.orderAmount = orderAmount;
    
        this.orderId = orderId;
        this.amount = amount;
    }

	

    public int getOrderId  () {
        return orderId;
    }

	

    public void setOrderId  (int orderId) {
        this.orderId = orderId;
    }

	

    public double getOrderAmount  () {
        return amount;
    }

	

    public void setOrderAmount  (double amount) {
        this.amount = amount;
    }

	
    private double amount;


}
