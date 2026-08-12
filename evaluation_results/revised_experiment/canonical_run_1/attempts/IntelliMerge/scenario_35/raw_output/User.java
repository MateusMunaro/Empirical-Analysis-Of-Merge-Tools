public class User {
    private String username;
    private int age;
    
    public void setAge(int age) {
<<<<<<< ours
        if (age < 0) {
            throw new IllegalArgumentException("Age cannot be negative");
=======
        if (age < 18 || age > 150) {
            throw new IllegalArgumentException("Age must be between 18 and 150");
>>>>>>> theirs
        }
        this.age = age;
    }
}