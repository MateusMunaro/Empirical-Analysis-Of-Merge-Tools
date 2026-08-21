public  class  UserPreferences {
	
    private String theme;

	
    private String language;

	

    public UserPreferences(String theme, String language) {
        this.theme = theme;
        this.language = language;
    }

	

    public String getTheme() {
        return theme;
    }

	

    public void setTheme(String theme) {
        this.theme = theme;
    }

	

    public String getLanguage() {
        return language;
    }

	

    public void setLanguage(String language) {
        this.language = language;
    }


}
