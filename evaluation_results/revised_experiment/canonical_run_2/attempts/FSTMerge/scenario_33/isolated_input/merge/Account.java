public  class  Account {
	
    private int accountId;

	
    private String username;

	
    private boolean active;

	

    public Account(int accountId, String username, boolean active) {
        this.accountId = accountId;
        this.username = username;
        this.active = active;
    }

	

    public int getAccountId() {
        return accountId;
    }

	

    public void setAccountId(int accountId) {
        this.accountId = accountId;
    }

	

    public String getUsername() {
        return username;
    }

	

    public void setUsername(String username) {
        this.username = username;
    }

	

    public boolean isActive() {
        return active;
    }

	

    public void setActive(boolean active) {
        this.active = active;
    }


}
