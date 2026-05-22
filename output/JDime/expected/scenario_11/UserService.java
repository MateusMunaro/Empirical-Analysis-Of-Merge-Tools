public class UserService {
    private DatabaseConnection db;
    private UserValidator validator;
    
    public UserService(DatabaseConnection db) {
        this.db = db;
        this.validator = new UserValidator();
    }
    
    public User createUser(String name, String email) {
        // Usando padrão Validator para validação (do RIGHT)
        ValidationResult result = validator.validate(name, email);
        if (!result.isValid()) {
            throw new IllegalArgumentException(result.getErrorMessage());
        }
        
        // Usando padrão Builder para criação do usuário (do LEFT)
        User user = new User.Builder()
            .withName(name)
            .withEmail(email)
            .withCreatedAt(new Date())
            .withStatus("ACTIVE")
            .build();
        
        // Salvamento no banco (adaptado para incluir status do LEFT)
        String sql = "INSERT INTO users (name, email, created_at, status) VALUES (?, ?, ?, ?)";
        db.execute(sql, user.getName(), user.getEmail(), user.getCreatedAt(), user.getStatus());
        
        return user;
    }
    
    public void updateUser(User user) {
        // Validação também no update (do RIGHT)
        ValidationResult result = validator.validate(user.getName(), user.getEmail());
        if (!result.isValid()) {
            throw new IllegalArgumentException(result.getErrorMessage());
        }
        
        String sql = "UPDATE users SET name = ?, email = ? WHERE id = ?";
        db.execute(sql, user.getName(), user.getEmail(), user.getId());
    }
    
    // Classe Builder interna (do LEFT)
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
    
    // Classe Validator (do RIGHT)
    private static class UserValidator {
        public ValidationResult validate(String name, String email) {
            if (name == null || name.trim().isEmpty()) {
                return new ValidationResult(false, "Nome não pode ser vazio");
            }
            if (name.length() < 2) {
                return new ValidationResult(false, "Nome deve ter pelo menos 2 caracteres");
            }
            if (email == null || !email.contains("@") || !email.contains(".")) {
                return new ValidationResult(false, "Email deve ter formato válido");
            }
            return new ValidationResult(true, null);
        }
    }
    
    private static class ValidationResult {
        private final boolean valid;
        private final String errorMessage;
        
        public ValidationResult(boolean valid, String errorMessage) {
            this.valid = valid;
            this.errorMessage = errorMessage;
        }
        
        public boolean isValid() {
            return valid;
        }
        
        public String getErrorMessage() {
            return errorMessage;
        }
    }
}