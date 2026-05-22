public class OrderService {
    private DatabaseConnection db;
    private AuditLogger auditLogger;
    
    public OrderService(DatabaseConnection db, AuditLogger auditLogger) {
        this.db = db;
        this.auditLogger = auditLogger;
    }
    
    public Order createOrder(OrderData orderData) {
        auditLogger.logOrderCreationAttempt(orderData.getCustomerId());
        
        try {
            // Validação monolítica (ainda não dividida no RIGHT)
            validateOrder(orderData);
            
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
    
    private void validateOrder(OrderData orderData) {
        // Mesma validação monolítica do BASE
        if (orderData.getCustomerId() <= 0) {
            throw new IllegalArgumentException("ID do cliente inválido");
        }
        
        if (orderData.getItems() == null || orderData.getItems().isEmpty()) {
            throw new IllegalArgumentException("Pedido deve ter pelo menos um item");
        }
        
        for (OrderItem item : orderData.getItems()) {
            if (item.getQuantity() <= 0) {
                throw new IllegalArgumentException("Quantidade deve ser positiva");
            }
            if (item.getPrice().compareTo(BigDecimal.ZERO) <= 0) {
                throw new IllegalArgumentException("Preço deve ser positivo");
            }
        }
        
        if (orderData.getShippingAddress() == null || 
            orderData.getShippingAddress().trim().isEmpty()) {
            throw new IllegalArgumentException("Endereço de entrega é obrigatório");
        }
        
        if (orderData.getPaymentMethod() == null) {
            throw new IllegalArgumentException("Método de pagamento é obrigatório");
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