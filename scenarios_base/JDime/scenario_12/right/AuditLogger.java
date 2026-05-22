public class AuditLogger {
    private DatabaseConnection auditDb;
    
    public AuditLogger(DatabaseConnection auditDb) {
        this.auditDb = auditDb;
    }
    
    public void logOrderCreationAttempt(Long customerId) {
        String sql = "INSERT INTO audit_log (action, customer_id, timestamp, details) VALUES (?, ?, ?, ?)";
        auditDb.execute(sql, "ORDER_CREATION_ATTEMPT", customerId, new Date(), 
                       "Customer attempted to create order");
    }
    
    public void logOrderCreated(Long orderId, Long customerId, BigDecimal amount) {
        String sql = "INSERT INTO audit_log (action, customer_id, timestamp, details) VALUES (?, ?, ?, ?)";
        auditDb.execute(sql, "ORDER_CREATED", customerId, new Date(), 
                       "Order " + orderId + " created with amount " + amount);
    }
    
    public void logOrderCreationFailed(Long customerId, String reason) {
        String sql = "INSERT INTO audit_log (action, customer_id, timestamp, details) VALUES (?, ?, ?, ?)";
        auditDb.execute(sql, "ORDER_CREATION_FAILED", customerId, new Date(), 
                       "Order creation failed: " + reason);
    }
}