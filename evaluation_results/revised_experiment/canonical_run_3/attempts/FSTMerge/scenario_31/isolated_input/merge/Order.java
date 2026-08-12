public   class  Order {
	
    private int orderId  ;

	
    private double amount  ;

	

    public Order(int orderId, double amount) {
        this.orderId = orderId;
        this.amount = amount;
    }

	

    public int getOrderId  () {
        return orderId;
    }

	

    public void setOrderId  (int orderId) {
        this.orderId = orderId;
    }

	

    public double getAmount  () {
        return amount;
    }

	

    public void setAmount  (double amount) {
        this.amount = amount;
    }

	
    private Date orderDate;

	 

    public Order(int orderId, double amount, Date orderDate) {
        this.orderId = orderId;
        this.amount = amount;
        this.orderDate = orderDate;
    }

	

    public Date getOrderDate() {
        return orderDate;
    }

	

    public void setOrderDate(Date orderDate) {
        this.orderDate = orderDate;
    }


}
