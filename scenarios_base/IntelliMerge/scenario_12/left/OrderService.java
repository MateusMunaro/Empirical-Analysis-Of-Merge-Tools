public class OrderService {
    private DatabaseConnection db;
    private CustomerValidator customerValidator;
    private ItemValidator itemValidator;
    private ShippingValidator shippingValidator;
    private PaymentValidator paymentValidator;
    
    public OrderService(DatabaseConnection db) {
        this.db = db;
        this.customerValidator = new CustomerValidator();
        this.itemValidator = new ItemValidator();
        this.shippingValidator = new ShippingValidator();
        this.paymentValidator = new PaymentValidator();
    }
    
    public Order createOrder(OrderData orderData) {
        // Validação distribuída em múltiplos validadores
        customerValidator.validate(orderData.getCustomerId());
        itemValidator.validate(orderData.getItems());
        shippingValidator.validate(orderData.getShippingAddress());
        paymentValidator.validate(orderData.getPaymentMethod());
        
        Order order = new Order();
        order.setCustomerId(orderData.getCustomerId());
        order.setItems(orderData.getItems());
        order.setShippingAddress(orderData.getShippingAddress());
        order.setPaymentMethod(orderData.getPaymentMethod());
        order.setTotalAmount(calculateTotal(orderData.getItems()));
        order.setCreatedAt(new Date());
        order.setStatus("PENDING");
        
        saveOrder(order);
        return order;
    }
    
    private BigDecimal calculateTotal(List<OrderItem> items) {
        return items.stream()
            .map(item -> item.getPrice().multiply(new BigDecimal(item.getQuantity())))
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
    
    private void saveOrder(Order order) {
        String sql = "INSERT INTO orders (customer_id, total_amount, status, created_at) VALUES (?, ?, ?, ?)";
        db.execute(sql, order.getCustomerId(), order.getTotalAmount(), 
                   order.getStatus(), order.getCreatedAt());
    }
}