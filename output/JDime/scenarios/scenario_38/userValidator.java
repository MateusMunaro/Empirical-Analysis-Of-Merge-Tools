
public class UserValidator {
  public boolean validateUser(String username, String email, int age) {
    if (username == null || username.trim().isEmpty() || username.length() < 3) {

<<<<<<< ./senarios_merge_base/JDime/scenario_38/left/userValidator.java
      throw new IllegalArgumentException("Username must be at least 3 characters long");
=======
      logValidationError("Username is null or empty");
>>>>>>> ./senarios_merge_base/JDime/scenario_38/right/userValidator.java
    }
    if (username.length() > 50) {
      logValidationError("Username too long");
      return false;
    }
    if (email == null || email.trim().isEmpty() || !isValidEmailFormat(email)) {

<<<<<<< ./senarios_merge_base/JDime/scenario_38/left/userValidator.java
      throw new IllegalArgumentException("Invalid email format");
=======
      logValidationError("Email is null or empty");
>>>>>>> ./senarios_merge_base/JDime/scenario_38/right/userValidator.java
    }
    if (!isValidBusinessEmail(email)) {
      logValidationError("Email domain not allowed");
      return false;
    }
    if (age < 
<<<<<<< ./senarios_merge_base/JDime/scenario_38/left/userValidator.java
    13
=======
    18
>>>>>>> ./senarios_merge_base/JDime/scenario_38/right/userValidator.java
     || age > 
<<<<<<< ./senarios_merge_base/JDime/scenario_38/left/userValidator.java
    120
=======
    100
>>>>>>> ./senarios_merge_base/JDime/scenario_38/right/userValidator.java
    ) {

<<<<<<< ./senarios_merge_base/JDime/scenario_38/left/userValidator.java
      throw new IllegalArgumentException("Age must be between 13 and 120");
=======
      logValidationError("Age not in valid range for business users");
>>>>>>> ./senarios_merge_base/JDime/scenario_38/right/userValidator.java

      return false;
    }
    if (
<<<<<<< ./senarios_merge_base/JDime/scenario_38/left/userValidator.java
    containsInvalidCharacters(username)
=======
    isRestrictedUsername(username)
>>>>>>> ./senarios_merge_base/JDime/scenario_38/right/userValidator.java
    ) {

<<<<<<< ./senarios_merge_base/JDime/scenario_38/left/userValidator.java
      throw new IllegalArgumentException("Username contains invalid characters");
=======
      logValidationError("Username is restricted");
>>>>>>> ./senarios_merge_base/JDime/scenario_38/right/userValidator.java
    }
    return true;
  }

  public boolean validatePassword(String password) {
    if (password == null || password.length() < 
<<<<<<< ./senarios_merge_base/JDime/scenario_38/left/userValidator.java
    8
=======
    10
>>>>>>> ./senarios_merge_base/JDime/scenario_38/right/userValidator.java
    ) {

<<<<<<< ./senarios_merge_base/JDime/scenario_38/left/userValidator.java
      throw new IllegalArgumentException("Password must be at least 8 characters long");
=======
      logValidationError("Password too short");
>>>>>>> ./senarios_merge_base/JDime/scenario_38/right/userValidator.java
    }
    if (!hasSpecialCharacter(password)) {
      logValidationError("Password must contain special character");
      return false;
    }

<<<<<<< ./senarios_merge_base/JDime/scenario_38/left/userValidator.java
    if (!hasUpperCase(password) || !hasLowerCase(password) || !hasDigit(password)) {
      throw new IllegalArgumentException("Password must contain uppercase, lowercase and digit");
    }
=======
    if (isCommonPassword(password)) {
      logValidationError("Password is too common");
      return false;
    }
>>>>>>> ./senarios_merge_base/JDime/scenario_38/right/userValidator.java

    return true;
  }

  public boolean validateEmail(String email) {
    if (email == null || !email.contains("@") || !email.contains(".")) {

<<<<<<< ./senarios_merge_base/JDime/scenario_38/left/userValidator.java
      throw new IllegalArgumentException("Email must contain @ and . symbols");
=======
      logValidationError("Email format invalid");
>>>>>>> ./senarios_merge_base/JDime/scenario_38/right/userValidator.java
    }
    if (email.length() > 100) {
      logValidationError("Email too long");
      return false;
    }

<<<<<<< ./senarios_merge_base/JDime/scenario_38/left/userValidator.java
    if (email.startsWith("@") || email.endsWith("@")) {
      throw new IllegalArgumentException("Email format is invalid");
    }
=======
    if (isDisposableEmail(email)) {
      logValidationError("Disposable email not allowed");
      return false;
    }
>>>>>>> ./senarios_merge_base/JDime/scenario_38/right/userValidator.java

    return true;
  }

  private boolean isValidEmailFormat(String email) {
    return email.matches("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$");
  }

  private boolean isValidBusinessEmail(String email) {
    String[] allowedDomains = { "company.com", "business.org", "enterprise.net" };
    for (String domain : allowedDomains) {
      if (email.endsWith("@" + domain)) {
        return true;
      }
    }
    return false;
  }

  private boolean containsInvalidCharacters(String username) {
    return username.matches(".*[<>\"\'&].*");
  }

  private boolean isRestrictedUsername(String username) {
    String[] restricted = { "admin", "root", "system", "test" };
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

  private boolean hasSpecialCharacter(String str) {
    return str.matches(".*[!@#$%^&*()_+\\-=\\[\\]{};\':\"\\\\|,.<>\\/?].*");
  }

  private boolean hasLowerCase(String str) {
    return str.matches(".*[a-z].*");
  }

  private boolean isCommonPassword(String password) {
    String[] common = { "password123", "123456789", "qwertyuiop" };
    for (String c : common) {
      if (password.toLowerCase().equals(c)) {
        return true;
      }
    }
    return false;
  }

  private boolean hasDigit(String str) {
    return str.matches(".*\\d.*");
  }

  private boolean isDisposableEmail(String email) {
    String[] disposable = { "10minutemail.com", "tempmail.org", "guerrillamail.com" };
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