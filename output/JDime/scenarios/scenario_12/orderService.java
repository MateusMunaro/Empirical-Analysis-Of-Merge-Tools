
public class OrderService {
  private DatabaseConnection db;

  private 
<<<<<<< ./senarios_merge_base/JDime/scenario_12/left/orderService.java
  CustomerValidator
=======
  AuditLogger
>>>>>>> ./senarios_merge_base/JDime/scenario_12/right/orderService.java
   
<<<<<<< ./senarios_merge_base/JDime/scenario_12/left/orderService.java
  customerValidator
=======
  auditLogger
>>>>>>> ./senarios_merge_base/JDime/scenario_12/right/orderService.java
  ;

  private ItemValidator itemValidator;

  private ShippingValidator shippingValidator;

  private PaymentValidator paymentValidator;

  public OrderService(DatabaseConnection db, AuditLogger auditLogger) {
    this.db = db;
    this.customerValidator = new CustomerValidator();
    this.itemValidator = new ItemValidator();
    this.shippingValidator = new ShippingValidator();

<<<<<<< ./senarios_merge_base/JDime/scenario_12/left/orderService.java
    this.paymentValidator = new PaymentValidator()
=======
    this.auditLogger = auditLogger
>>>>>>> ./senarios_merge_base/JDime/scenario_12/right/orderService.java
    ;
  }

  public Order createOrder(OrderData orderData) {
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

<<<<<<< ./senarios_merge_base/JDime/scenario_12/left/orderService.java
    order
=======
    auditLogger
>>>>>>> ./senarios_merge_base/JDime/scenario_12/right/orderService.java
    .
<<<<<<< ./senarios_merge_base/JDime/scenario_12/left/orderService.java
    setStatus("PENDING")
=======
    logOrderCreationAttempt(orderData.getCustomerId())
>>>>>>> ./senarios_merge_base/JDime/scenario_12/right/orderService.java
    ;

<<<<<<< ./senarios_merge_base/JDime/scenario_12/left/orderService.java
    saveOrder(order);
=======
    try {
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
>>>>>>> ./senarios_merge_base/JDime/scenario_12/right/orderService.java

    return order;
  }

  private void validateOrder(OrderData orderData) {
    if (orderData.getCustomerId() <= 0) {
      throw new IllegalArgumentException("ID do cliente inv\u00e1lido");
    }
    if (orderData.getItems() == null || orderData.getItems().isEmpty()) {
      throw new IllegalArgumentException("Pedido deve ter pelo menos um item");
    }
    for (OrderItem item : orderData.getItems()) {
      if (item.getQuantity() <= 0) {
        throw new IllegalArgumentException("Quantidade deve ser positiva");
      }
      if (item.getPrice().compareTo(BigDecimal.ZERO) <= 0) {
        throw new IllegalArgumentException("Pre\u00e7o deve ser positivo");
      }
    }
    if (orderData.getShippingAddress() == null || orderData.getShippingAddress().trim().isEmpty()) {
      throw new IllegalArgumentException("Endere\u00e7o de entrega \u00e9 obrigat\u00f3rio");
    }
    if (orderData.getPaymentMethod() == null) {
      throw new IllegalArgumentException("M\u00e9todo de pagamento \u00e9 obrigat\u00f3rio");
    }
  }

  private BigDecimal calculateTotal(List<OrderItem> items) {
    return items.stream().map((item) -> item.getPrice().multiply(new BigDecimal(item.getQuantity()))).reduce(BigDecimal.ZERO, BigDecimal::add);
  }

  private void saveOrder(Order order) {
    String sql = "INSERT INTO orders (customer_id, total_amount, status, created_at) VALUES (?, ?, ?, ?)";
    db.execute(sql, order.getCustomerId(), order.getTotalAmount(), order.getStatus(), order.getCreatedAt());
  }
}