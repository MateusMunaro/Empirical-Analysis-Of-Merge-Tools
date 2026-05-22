public class PersonContact {
    private String email; 
    private String phone;
    private String socialMedia; 

    public PersonContact(String email, String phone, String socialMedia) {
        this.email = email;
        this.phone = phone;
        this.socialMedia = socialMedia;
    }

    public String getEmail() {
        return email;
    }
    
    public void setEmail(String email) {
        this.email = email;
    }
    
    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getSocialMedia() {
        return socialMedia;
    }

    public void setSocialMedia(String socialMedia) {
        this.socialMedia = socialMedia;
    }
}