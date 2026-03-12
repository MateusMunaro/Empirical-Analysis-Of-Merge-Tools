public class Organization {
    private String deptName;
    private String location;

    public Organization(String deptName, String location) {
        this.deptName = deptName;
        this.location = location;
    }

    public String getDeptName() {
        return deptName;
    }

    public void setDeptName(String deptName) {
        this.deptName = deptName;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }
}