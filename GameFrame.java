import javax.swing.*;

public class GameFrame extends JFrame {

    GameFrame() {

        this.add(new GamePanel());
        this.setTitle("You are offline check your internet connection, if you are connected internet then restart application");
        this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        this.setResizable(false);
        this.pack();
        this.setVisible(true);
        this.setLocationRelativeTo(null);

    }
}
