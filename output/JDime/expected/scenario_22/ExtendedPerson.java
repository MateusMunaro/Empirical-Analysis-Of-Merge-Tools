public class ExtendedPerson {
    private String nationality;
    private String profession; 

    public ExtendedPerson(String nationality, String profession) {
        this.nationality = nationality;
        this.profession = profession;
    }

    public String getNationality() {
        return nationality;
    }

    public void setNationality(String nationality) {
        this.nationality = nationality;
    }

    public String getProfession() {
        return profession;
    }

    public void setProfession(String profession) {
        this.profession = profession;
    }
}
