public class UserValidator {
    
    public boolean validateUser(String username, String email, int age) {
        // Enhanced validation with multiple checks
        if (username == null || username.trim().isEmpty() || username.length() < 3) {
            throw new IllegalArgumentException("Username must be at least 3 characters long");
        }
        if (email == null || email.trim().isEmpty() || !isValidEmailFormat(email)) {
            throw new IllegalArgumentException("Invalid email format");
        }
        if (age < 13 || age > 120) {
            throw new IllegalArgumentException("Age must be between 13 and 120");
        }
        if (containsInvalidCharacters(username)) {
            throw new IllegalArgumentException("Username contains invalid characters");
        }
        return true;
    }
    
    public boolean validatePassword(String password) {
        if (password == null || password.length() < 8) {
            throw new IllegalArgumentException("Password must be at least 8 characters long");
        }
        if (!hasUpperCase(password) || !hasLowerCase(password) || !hasDigit(password)) {
            throw new IllegalArgumentException("Password must contain uppercase, lowercase and digit");
        }
        return true;
    }
    
    public boolean validateEmail(String email) {
        if (email == null || !email.contains("@") || !email.contains(".")) {
            throw new IllegalArgumentException("Email must contain @ and . symbols");
        }
        if (email.startsWith("@") || email.endsWith("@")) {
            throw new IllegalArgumentException("Email format is invalid");
        }
        return true;
    }
    
    private boolean isValidEmailFormat(String email) {
        return email.matches("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$");
    }
    
    private boolean containsInvalidCharacters(String username) {
        return username.matches(".*[<>\"'&].*");
    }
    
    private boolean hasUpperCase(String str) {
        return str.matches(".*[A-Z].*");
    }
    
    private boolean hasLowerCase(String str) {
        return str.matches(".*[a-z].*");
    }
    
    private boolean hasDigit(String str) {
        return str.matches(".*\\d.*");
    }
}