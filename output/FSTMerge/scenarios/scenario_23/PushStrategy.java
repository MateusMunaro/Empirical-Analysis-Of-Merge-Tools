public  class  PushStrategy  implements NotificationStrategy {
	
    @Override
    public void send(String message, String recipient) {
        System.out.println("Enviando push notification para: " + recipient);
        System.out.println("Mensagem: " + message);
        System.out.println("Push enviado!");
    }


}
