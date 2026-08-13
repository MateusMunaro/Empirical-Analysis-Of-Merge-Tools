public class SmsStrategy implements NotificationStrategy {
    @Override
    public void send(String message, String recipient) {
        System.out.println("Enviando SMS para: " + recipient);
        System.out.println("Texto: " + message);
        System.out.println("SMS enviado!");
    }
}