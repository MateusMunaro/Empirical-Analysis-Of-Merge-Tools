public class EmailStrategy implements NotificationStrategy {
    @Override
    public void send(String message, String recipient) {
        System.out.println("Enviando email para: " + recipient);
        System.out.println("Conteúdo: " + message);
        System.out.println("Email enviado com sucesso!");
    }
}