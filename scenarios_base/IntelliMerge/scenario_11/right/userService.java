public class UserService {
    private DatabaseConnection db;
    private UserValidator validator;
    
    public UserService(DatabaseConnection db) {
        this.db = db;
        this.validator = new UserValidator();
    }
    
    public User createUser(String name, String email) {
        // Usando padrão Validator para validação
        ValidationResult result = validator.validate(name, email);
        if (!result.isValid()) {
            throw new IllegalArgumentException(result.getErrorMessage());
        }
        
        // Criação do usuário
        User user = new User();
        user.setName(name);
        user.setEmail(email);
        user.setCreatedAt(new Date());
        
        // Salvamento no banco
        String sql = "INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)";
        db.execute(sql, user.getName(), user.getEmail(), user.getCreatedAt());
        
        return user;
    }
    
    public void updateUser(User user) {
        // Validação também no update
        ValidationResult result = validator.validate(user.getName(), user.getEmail());
        if (!result.isValid()) {
            throw new IllegalArgumentException(result.getErrorMessage());
        }
        
        String sql = "UPDATE users SET name = ?, email = ? WHERE id = ?";
        db.execute(sql, user.getName(), user.getEmail(), user.getId());
    }
    
    // Classe Validator
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