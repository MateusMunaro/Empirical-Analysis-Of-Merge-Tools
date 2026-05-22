public  class  Client {
	
    private int id;

	 
    private String name;

	
    private int purchaseId;

	 

    public Client(int id, String name, int purchaseId) {
        this.id = id;
        this.name = name;
        this.purchaseId = purchaseId;
    }

	

    public int getId() {
        return id;
    }

	

    public void setId(int id) {
        this.id = id;
    }

	

    public String getName() {
        return name;
    }

	

    public void setName(String name) {
        this.name = name;
    }

	

    public int getPurchaseId() {
        return purchaseId;
    }

	

    public void setPurchaseId(int purchaseId) {
        this.purchaseId = purchaseId;
    }


}
