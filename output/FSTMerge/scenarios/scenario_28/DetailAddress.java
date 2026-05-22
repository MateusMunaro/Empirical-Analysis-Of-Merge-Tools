public  class  DetailedAddress {
	
    private String street;

	
    private String district;

	

    public DetailedAddress(String street, String district) {
        this.street = street;
        this.district = district;
    }

	

    public String getStreet() {
        return street;
    }

	

    public String getDistrict() {
        return district;
    }

	

    public void setStreet(String street) {
        this.street = street;
    }

	
    
    public void setDistrict(String district) {
        this.district = district;
    }


}
