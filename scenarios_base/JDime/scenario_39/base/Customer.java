public class Customer {
    private Long id;
    private String name;
    private String email;
    private String status;
    
    public Customer(Long id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.status = "ACTIVE";
    }
    
    public Long getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public String getStatus() { return status; }
    
    public void setStatus(String status) {
        this.status = status;
    }
    
    public double calculateDiscount(double amount) {
        return amount * 0.05; // 5% discount for all customers
    }
}
