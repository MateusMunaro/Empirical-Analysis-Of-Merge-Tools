public class OrderService {
    private DatabaseConnection db;
    
    public OrderService(DatabaseConnection db) {
        this.db = db;
    }
    
    public Order createOrder(OrderData orderData) {
        // Validação monolítica em um só lugar
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
        return order;
    }
    
    private void validateOrder(OrderData orderData) {
        // Todas as validações em um método
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
