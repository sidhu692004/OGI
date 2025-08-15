import java.awt.*;
import java.awt.event.*;
import java.util.Random;
import javax.swing.*;


public class GamePanel extends JPanel implements ActionListener {
    static final int SCREEN_WIDTH = 1550;
    static final int SCREEN_HEIGHT = 780;
    static final int UNIT_SIZE = 30;
    static final int GAME_UNITS = (SCREEN_WIDTH * SCREEN_HEIGHT)/ UNIT_SIZE;
    static final int DELAY = 200;
    final int x[] = new int[GAME_UNITS];
    final int y[] = new int[GAME_UNITS];
    int bodyParts = 3;
    int applesEaten;
    int appleX;
    int appleY;
    char direction = 'R';
    boolean running = false;
    Timer timer;
    Random random;
    JButton replayButton;




    GamePanel() {
        random = new Random();
        this.setPreferredSize(new Dimension(SCREEN_WIDTH,SCREEN_HEIGHT));
        this.setBackground(Color.black);
        this.setFocusable(true);
        this.addKeyListener(new MyKeyAdapter());
        startGame();
    }
    public Action startGame() {
        newApple();
        running = true;
        timer = new Timer(DELAY,this);
        timer.start();

        return null;
    }
    public void paintComponent(Graphics g) {
        super.paintComponent(g);
        draw(g);

    }
    public void draw(Graphics g) {
        if (running) {
            // Draw grid lines
            for (int i = 0; i < SCREEN_WIDTH / UNIT_SIZE; i++) {
                g.drawLine(i * UNIT_SIZE, 0, i * UNIT_SIZE, SCREEN_HEIGHT); // Vertical lines across the screen height
            }
            for (int i = 0; i < SCREEN_HEIGHT / UNIT_SIZE; i++) {
                g.drawLine(0, i * UNIT_SIZE, SCREEN_WIDTH, i * UNIT_SIZE);  // Horizontal lines across the screen width
            }
    
            // Draw apple
            g.setColor(Color.red);
            g.fillOval(appleX, appleY, UNIT_SIZE, UNIT_SIZE);
    
            // Draw snake
            for (int i = 0; i < bodyParts; i++) {
                if (i == 0) {
                    g.setColor(Color.BLUE);
                    g.fillRect(x[i], y[i], UNIT_SIZE, UNIT_SIZE);
                } else {
                    g.setColor(Color.GREEN);
                    g.fillRect(x[i], y[i], UNIT_SIZE, UNIT_SIZE);
                }
            }
    
            // Draw score
            g.setColor(Color.white);
            g.setFont(new Font("Minecraftia", Font.BOLD, 25));
            FontMetrics metrics = getFontMetrics(g.getFont());
            g.drawString("Score: " + applesEaten, (SCREEN_WIDTH - metrics.stringWidth("Score: " + applesEaten)) / 2, g.getFont().getSize());
        } else {
            gameOver(g);
        }
    }
    

    public void newApple() {
        appleX = random.nextInt((int)(SCREEN_WIDTH/UNIT_SIZE))*UNIT_SIZE;
        appleY = random.nextInt((int)(SCREEN_HEIGHT/UNIT_SIZE))*UNIT_SIZE;

    }
    public void move() {
        for(int i=bodyParts; i>0;i--) {
            x[i] = x[i-1];
            y[i] = y[i-1];

        }

        switch(direction) {
            case 'U':
                y[0]= y[0] - UNIT_SIZE;
                break;
            case 'D':
                y[0]= y[0] + UNIT_SIZE;
                break;
            case 'L':
                x[0]= x[0] - UNIT_SIZE;
                break;
            case 'R':
                x[0]= x[0] + UNIT_SIZE;
                break;
        }
    }
    public void checkApple() {
        if((x[0] == appleX) && (y[0]== appleY)) {
            bodyParts++;
            applesEaten++;
            newApple();
        }

    }
    public void checkCollisions() {
        //checks if head collides with body
        for(int i = bodyParts; i> 0; i--) {
            if((x[0]== x[i]) && (y[0]==y[i])) {
                running =false;
            }
        }
        //check if head touches left border
        if(x[0] < 0) {
            running = false;
        }
        //check if head touches right border
        if(x[0] > SCREEN_WIDTH) {
            running = false;
        }
        //check if head touches top border
        if(y[0] < 0) {
            running = false;
        }
        //check if head touches bottom borer
        if(y[0] > SCREEN_HEIGHT) {
            running = false;
        }

        if(running == false) {
            timer.stop();
        }
    }
    public void gameOver(Graphics g) {
        // Draw the "Game Over" text
        g.setColor(Color.red);
        g.setFont(new Font("Minecraftia", Font.BOLD, 50));
        FontMetrics metrics1 = getFontMetrics(g.getFont());
        g.drawString("Game Over", (SCREEN_WIDTH - metrics1.stringWidth("Game Over")) / 2, SCREEN_HEIGHT / 2);
    
        // Debugging: Print score details
        System.out.println("Game Over! Score: " + applesEaten);
        
        // Draw the score
        g.setColor(Color.white);
        g.setFont(new Font("Minecraftia", Font.BOLD, 25));
        FontMetrics metrics2 = getFontMetrics(g.getFont());
        int scoreX = (SCREEN_WIDTH - metrics2.stringWidth("Score: " + applesEaten)) / 2;
        int scoreY = g.getFont().getSize() + 50;
        
        System.out.println("Drawing score at: " + scoreX + ", " + scoreY);
        g.drawString("Your Score: " + applesEaten, scoreX, scoreY);
    
        // Check if the replay button is already added
        if (replayButton == null) {
            // Create the "Replay" button
            replayButton = new JButton("Replay");
            replayButton.setBounds(SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT / 2 + 50, 100, 40);
            replayButton.addActionListener(new ActionListener() {
                @Override
                public void actionPerformed(ActionEvent e) {
                    replayGame();
                }
            });
    
            this.add(replayButton);  // Add the button to the JPanel
            this.repaint(); // Repaint to ensure the button appears
        }
    }
    
    public void replayGame() {
        this.add(new GameFrame());
    }
    public void endingScreen(Graphics g) {
        g.setColor(Color.red);
        g.setFont(new Font("Minecraftia", Font.BOLD, 50));
        FontMetrics metrics1 = getFontMetrics(g.getFont());
        g.drawString("Game Over", (SCREEN_WIDTH - metrics1.stringWidth("Game Over")) /2, SCREEN_HEIGHT /2);

        g.setColor(Color.white);
        g.setFont(new Font("Minecraftia", Font.BOLD, 25));
        FontMetrics metrics2 = getFontMetrics(g.getFont());
        g.drawString("Score: "+applesEaten, (SCREEN_WIDTH - metrics2.stringWidth("Score: "+applesEaten)) /2, g.getFont().getSize());
        replayButton = new JButton("Replay");


    }
    public void endFrame() {
        JFrame endFrame = new JFrame();
        JPanel endPanel = new JPanel();
        JButton replayButton = new JButton("Replay");
        replayButton.addActionListener(this);

        JLabel endLabel = new JLabel();

        // endPanel.setBorder(BorderFactory.createEmptyBorder(60,60,4,60));
        endPanel.setLayout(new GridLayout(0,1));
        endPanel.add(replayButton);
        endPanel.add(endLabel);

        endFrame.add(endPanel, BorderLayout.CENTER);
        endFrame.setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
        endFrame.setTitle("Snake");
        endFrame.pack();
        endFrame.setVisible(true);
    }

    @Override
    public void actionPerformed(ActionEvent e) {
        if(running) {
            move();
            checkApple();
            checkCollisions();
            repaint();
        } else {
        }
    }
    public class MyKeyAdapter extends KeyAdapter{
        @Override
        public void keyPressed(KeyEvent e) {
            switch(e.getKeyCode()) {
                case KeyEvent.VK_LEFT :
                    if(direction != 'R') {
                        direction = 'L';
                        break;
                    }
                case KeyEvent.VK_RIGHT:
                    if(direction != 'L') {
                        direction = 'R';
                        break;
                    }
                case KeyEvent.VK_UP :
                    if(direction != 'D') {
                        direction = 'U';
                        break;
                    }
                case KeyEvent.VK_DOWN :
                    if(direction != 'U') {
                        direction = 'D';
                        break;
                    }
            }
        }
    }
}
