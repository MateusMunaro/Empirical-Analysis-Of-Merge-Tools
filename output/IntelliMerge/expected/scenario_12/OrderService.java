public class OrderService {
    private DatabaseConnection db;
    private AuditLogger auditLogger;
    private CustomerValidator customerValidator;
    private ItemValidator itemValidator;
    private ShippingValidator shippingValidator;
    private PaymentValidator paymentValidator;
    
    public OrderService(DatabaseConnection db, AuditLogger auditLogger) {
        this.db = db;
        this.auditLogger = auditLogger;
        this.customerValidator = new CustomerValidator();
        this.itemValidator = new ItemValidator();
        this.shippingValidator = new ShippingValidator();
        this.paymentValidator = new PaymentValidator();
    }
    
    public Order createOrder(OrderData orderData) {
        auditLogger.logOrderCreationAttempt(orderData.getCustomerId());
        
        try {
            // Validação distribuída em múltiplos validadores (do LEFT)
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
            
            auditLogger.logOrderCreated(order.getId(), order.getCustomerId(), order.getTotalAmount());
            return order;
            
        } catch (Exception e) {
            auditLogger.logOrderCreationFailed(orderData.getCustomerId(), e.getMessage());
            throw e;
        }
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