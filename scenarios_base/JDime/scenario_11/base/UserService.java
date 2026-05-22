

public class UserService {
    private DatabaseConnection db;
    
    public UserService(DatabaseConnection db) {
        this.db = db;
    }
    
    public User createUser(String name, String email) {
        // Validação básica
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("Nome não pode ser vazio");
        }
        if (email == null || !email.contains("@")) {
            throw new IllegalArgumentException("Email inválido");
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
        String sql = "UPDATE users SET name = ?, email = ? WHERE id = ?";
        db.execute(sql, user.getName(), user.getEmail(), user.getId());
    }
}