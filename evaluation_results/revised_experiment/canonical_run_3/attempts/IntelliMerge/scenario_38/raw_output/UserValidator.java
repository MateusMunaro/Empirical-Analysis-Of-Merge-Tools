public class UserValidator {

    public boolean validateUser(String username, String email, int age) {
<<<<<<< ours
        // Enhanced validation with multiple checks
        if (username == null || username.trim().isEmpty() || username.length() < 3) {
            throw new IllegalArgumentException("Username must be at least 3 characters long");
=======
        // Different validation approach with logging
        if (username == null || username.isEmpty()) {
            logValidationError("Username is null or empty");
            return false;
        }
        if (username.length() > 50) {
            logValidationError("Username too long");
            return false;
>>>>>>> theirs
        }
<<<<<<< ours
        if (email == null || email.trim().isEmpty() || !isValidEmailFormat(email)) {
            throw new IllegalArgumentException("Invalid email format");
=======
        if (email == null || email.isEmpty()) {
            logValidationError("Email is null or empty");
            return false;
>>>>>>> theirs
        }
<<<<<<< ours
        if (age < 13 || age > 120) {
            throw new IllegalArgumentException("Age must be between 13 and 120");
        }
        if (containsInvalidCharacters(username)) {
            throw new IllegalArgumentException("Username contains invalid characters");
=======
        if (!isValidBusinessEmail(email)) {
            logValidationError("Email domain not allowed");
            return false;
        }
        if (age < 18 || age > 100) {
            logValidationError("Age not in valid range for business users");
            return false;
        }
        if (isRestrictedUsername(username)) {
            logValidationError("Username is restricted");
            return false;
>>>>>>> theirs
        }
        return true;
    }
    
    public boolean validatePassword(String password) {
<<<<<<< ours
        if (password == null || password.length() < 8) {
            throw new IllegalArgumentException("Password must be at least 8 characters long");
        }
        if (!hasUpperCase(password) || !hasLowerCase(password) || !hasDigit(password)) {
            throw new IllegalArgumentException("Password must contain uppercase, lowercase and digit");
=======
        if (password == null || password.length() < 10) {
            logValidationError("Password too short");
            return false;
        }
        if (!hasSpecialCharacter(password)) {
            logValidationError("Password must contain special character");
            return false;
        }
        if (isCommonPassword(password)) {
            logValidationError("Password is too common");
            return false;
>>>>>>> theirs
        }
        return true;
    }
    
    public boolean validateEmail(String email) {
<<<<<<< ours
        if (email == null || !email.contains("@") || !email.contains(".")) {
            throw new IllegalArgumentException("Email must contain @ and . symbols");
        }
        if (email.startsWith("@") || email.endsWith("@")) {
            throw new IllegalArgumentException("Email format is invalid");
=======
        if (email == null || !email.contains("@")) {
            logValidationError("Email format invalid");
            return false;
        }
        if (email.length() > 100) {
            logValidationError("Email too long");
            return false;
        }
        if (isDisposableEmail(email)) {
            logValidationError("Disposable email not allowed");
            return false;
>>>>>>> theirs
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
    private boolean isValidBusinessEmail(String email) {
        String[] allowedDomains = {"company.com", "business.org", "enterprise.net"};
        for (String domain : allowedDomains) {
            if (email.endsWith("@" + domain)) {
                return true;
            }
        }
        return false;
    }
    
    private boolean isRestrictedUsername(String username) {
        String[] restricted = {"admin", "root", "system", "test"};
        for (String r : restricted) {
            if (username.toLowerCase().contains(r)) {
                return true;
            }
        }
        return false;
    }
    
    private boolean hasSpecialCharacter(String str) {
        return str.matches(".*[!@#$%^&*()_+\\-=\\[\\]{};':\"\\\\|,.<>\\/?].*");
    }
    
    private boolean isCommonPassword(String password) {
        String[] common = {"password123", "123456789", "qwertyuiop"};
        for (String c : common) {
            if (password.toLowerCase().equals(c)) {
                return true;
            }
        }
        return false;
    }
    
    private boolean isDisposableEmail(String email) {
        String[] disposable = {"10minutemail.com", "tempmail.org", "guerrillamail.com"};
        for (String d : disposable) {
            if (email.endsWith("@" + d)) {
                return true;
            }
        }
        return false;
    }
    
    private void logValidationError(String message) {
        System.err.println("Validation Error: " + message);
    }
}