public   class  UserValidator {
	
    
    public boolean validateUser  (String username, String email, int age) {
        // Different validation approach with logging
        if (username == null || username.isEmpty()) {
            logValidationError("Username is null or empty");
            return false;
        }
        if (username.length() > 50) {
            logValidationError("Username too long");
            return false;
        }
        if (email == null || email.isEmpty()) {
            logValidationError("Email is null or empty");
            return false;
        }
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
        }
        return true;
    }

	
    
    public boolean validatePassword  (String password) {
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
        }
        return true;
    }

	
    
    public boolean validateEmail(String email) {
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
