public class UserValidator {
    
    public boolean validateUser(String username, String email, int age) {
        if (username == null || username.isEmpty()) {
            return false;
        }
        if (email == null || email.isEmpty()) {
            return false;
        }
        if (age < 0) {
            return false;
        }
        return true;
    }
    
    public boolean validatePassword(String password) {
        if (password == null || password.length() < 6) {
            return false;
        }
        return true;
    }
    
    public boolean validateEmail(String email) {
        if (email == null || !email.contains("@")) {
            return false;
        }
        return true;
    }
}