public class UserValidator {
    private boolean throwExceptions = false;
    private boolean enableLogging = true;
    
    public UserValidator() {
        this(false, true);
    }
    
    public UserValidator(boolean throwExceptions, boolean enableLogging) {
        this.throwExceptions = throwExceptions;
        this.enableLogging = enableLogging;
    }
    
    public boolean validateUser(String username, String email, int age) {
        // Username validation
        if (username == null || username.trim().isEmpty()) {
            return handleValidationError("Username is null or empty");
        }
        if (username.length() < 3) {
            return handleValidationError("Username must be at least 3 characters long");
        }
        if (username.length() > 50) {
            return handleValidationError("Username too long");
        }
        if (containsInvalidCharacters(username)) {
            return handleValidationError("Username contains invalid characters");
        }
        if (isRestrictedUsername(username)) {
            return handleValidationError("Username is restricted");
        }
        
        // Email validation
        if (email == null || email.trim().isEmpty()) {
            return handleValidationError("Email is null or empty");
        }
        if (!isValidEmailFormat(email)) {
            return handleValidationError("Invalid email format");
        }
        
        // Age validation - combining both ranges
        if (age < 13 || age > 120) {
            return handleValidationError("Age must be between 13 and 120");
        }
        
        return true;
    }
    
    public boolean validatePassword(String password) {
        if (password == null) {
            return handleValidationError("Password cannot be null");
        }
        if (password.length() < 10) {
            return handleValidationError("Password must be at least 10 characters long");
        }
        if (!hasUpperCase(password) || !hasLowerCase(password) || !hasDigit(password)) {
            return handleValidationError("Password must contain uppercase, lowercase and digit");
        }
        if (!hasSpecialCharacter(password)) {
            return handleValidationError("Password must contain special character");
        }
        if (isCommonPassword(password)) {
            return handleValidationError("Password is too common");
        }
        return true;
    }
    
    public boolean validateEmail(String email) {
        if (email == null || !email.contains("@") || !email.contains(".")) {
            return handleValidationError("Email must contain @ and . symbols");
        }
        if (email.startsWith("@") || email.endsWith("@")) {
            return handleValidationError("Email format is invalid");
        }
        if (email.length() > 100) {
            return handleValidationError("Email too long");
        }
        if (isDisposableEmail(email)) {
            return handleValidationError("Disposable email not allowed");
        }
        return true;
    }
    
    // Business-specific validation
    public boolean validateBusinessUser(String username, String email, int age) {
        if (!validateUser(username, email, age)) {
            return false;
        }
        if (!isValidBusinessEmail(email)) {
            return handleValidationError("Email domain not allowed for business users");
        }
        if (age < 18 || age > 100) {
            return handleValidationError("Age not in valid range for business users");
        }
        return true;
    }
    
    private boolean handleValidationError(String message) {
        if (enableLogging) {
            logValidationError(message);
        }
        if (throwExceptions) {
            throw new IllegalArgumentException(message);
        }
        return false;
    }
    
    private boolean isValidEmailFormat(String email) {
        return email.matches("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$");
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
    
    private boolean containsInvalidCharacters(String username) {
        return username.matches(".*[<>\"'&].*");
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
    
    private boolean hasUpperCase(String str) {
        return str.matches(".*[A-Z].*");
    }
    
    private boolean hasLowerCase(String str) {
        return str.matches(".*[a-z].*");
    }
    
    private boolean hasDigit(String str) {
        return str.matches(".*\\d.*");
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