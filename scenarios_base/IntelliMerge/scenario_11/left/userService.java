public class UserService {
    private DatabaseConnection db;
    
    public UserService(DatabaseConnection db) {
        this.db = db;
    }
    
    public User createUser(String name, String email) {
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("Nome não pode ser vazio");
        }
        if (email == null || !email.contains("@")) {
            throw new IllegalArgumentException("Email inválido");
        }
        
        User user = new User.Builder()
            .withName(name)
            .withEmail(email)
            .withCreatedAt(new Date())
            .withStatus("ACTIVE")
            .build();
        
        String sql = "INSERT INTO users (name, email, created_at, status) VALUES (?, ?, ?, ?)";
        db.execute(sql, user.getName(), user.getEmail(), user.getCreatedAt(), user.getStatus());
        
        return user;
    }
    
    public void updateUser(User user) {
        String sql = "UPDATE users SET name = ?, email = ? WHERE id = ?";
        db.execute(sql, user.getName(), user.getEmail(), user.getId());
    }
    
    public static class UserBuilder {
        private String name;
        private String email;
        private Date createdAt;
        private String status;
        
        public UserBuilder withName(String name) {
            this.name = name;
            return this;
        }
        
        public UserBuilder withEmail(String email) {
            this.email = email;
            return this;
        }
        
        public UserBuilder withCreatedAt(Date createdAt) {
            this.createdAt = createdAt;
            return this;
        }
        
        public UserBuilder withStatus(String status) {
            this.status = status;
            return this;
        }
        
        public User build() {
            User user = new User();
            user.setName(this.name);
            user.setEmail(this.email);
            user.setCreatedAt(this.createdAt);
            user.setStatus(this.status != null ? this.status : "ACTIVE");
            return user;
        }
    }
}