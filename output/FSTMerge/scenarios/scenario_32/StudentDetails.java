public  class  StudentDetails {
	
    private int age;

	
    private List<String> enrolledCourses;

	

    public StudentDetails(int age, List<String> enrolledCourses) {
        this.age = age;
        this.enrolledCourses = enrolledCourses;
    }

	

    public int getAge() {
        return age;
    }

	

    public void setAge(int age) {
        this.age = age;
    }

	

    public List<String> getEnrolledCourses() {
        return enrolledCourses;
    }

	

    public void setEnrolledCourses(List<String> enrolledCourses) {
        this.enrolledCourses = enrolledCourses;
    }


}
