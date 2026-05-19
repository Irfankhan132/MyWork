package sem_project;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Font;
import java.awt.Image;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.Timer;
import javax.swing.border.EmptyBorder;
import static sem_project.Client.dout;
import java.util.Calendar;
import java.text.SimpleDateFormat;
import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.JOptionPane;
import javax.swing.JScrollPane;
import static sem_project.Client.vertical;

public class Server implements ActionListener {

    JPanel p1;
    JTextField text_Field;
    JButton btn;
    static JPanel message_area;

    static JFrame frame = new JFrame("Chatting Application");

    static Box vertical = Box.createVerticalBox();

    static ServerSocket skt;
    static Socket s;

    static DataInputStream din;
    static DataOutputStream dout;

    boolean typing;

    Server() {

        p1 = new JPanel();
        p1.setLayout(null);
        // p1.setBackground(Color.BLUE);
        p1.setBackground(new Color(7, 44, 84));
        p1.setBounds(0, 0, 450, 70);
        frame.add(p1);

        ImageIcon i4 = new ImageIcon(ClassLoader.getSystemResource("Sem_Project/icons/irfan.png"));
        Image i5 = i4.getImage().getScaledInstance(60, 60, Image.SCALE_DEFAULT);
        ImageIcon i6 = new ImageIcon(i5);
        JLabel l2 = new JLabel(i6);
        l2.setBounds(40, 5, 60, 60);
        p1.add(l2);

        ImageIcon i7 = new ImageIcon(ClassLoader.getSystemResource("Sem_Project/icons/video.png"));
        Image i8 = i7.getImage().getScaledInstance(30, 30, Image.SCALE_DEFAULT);
        ImageIcon i9 = new ImageIcon(i8);
        JLabel l5 = new JLabel(i9);
        l5.setBounds(290, 20, 30, 30);
        p1.add(l5);

        ImageIcon i11 = new ImageIcon(ClassLoader.getSystemResource("Sem_Project/icons/phone.png"));
        Image i12 = i11.getImage().getScaledInstance(35, 30, Image.SCALE_DEFAULT);
        ImageIcon i13 = new ImageIcon(i12);
        JLabel l6 = new JLabel(i13);
        l6.setBounds(350, 20, 35, 30);
        p1.add(l6);

        ImageIcon i14 = new ImageIcon(ClassLoader.getSystemResource("Sem_Project/icons/options.png"));
        Image i15 = i14.getImage().getScaledInstance(13, 25, Image.SCALE_DEFAULT);
        ImageIcon i16 = new ImageIcon(i15);
        JLabel l7 = new JLabel(i16);
        l7.setBounds(410, 20, 13, 25);
        p1.add(l7);

        JLabel l3 = new JLabel("Irfan Khan");
        l3.setFont(new Font("SAN_SERIF", Font.BOLD, 18));
        l3.setForeground(Color.WHITE);
        l3.setBounds(110, 15, 100, 18);
        p1.add(l3);

        JLabel l4 = new JLabel("Active Now");
        l4.setFont(new Font("SAN_SERIF", Font.PLAIN, 14));
        l4.setForeground(Color.WHITE);
        l4.setBounds(110, 35, 100, 20);
        p1.add(l4);

        Timer t = new Timer(1, new ActionListener() {
            public void actionPerformed(ActionEvent ae) {
                if (!typing) {
                    l4.setText("Active Now");
                }
            }
        });

        t.setInitialDelay(2000);

        message_area = new JPanel();
        //a1.setBounds(5, 75, 425, 530);
        message_area.setFont(new Font("SAN_SERIF", Font.PLAIN, 16));
        //a1.setBackground(Color.WHITE);
        //a1.setEditable(false);
        //a1.setLineWrap(true);
        //a1.setWrapStyleWord(true);
        //f1.add(message_area);

        JScrollPane sp = new JScrollPane(message_area);
        sp.setBounds(5, 75, 425, 530);
        sp.setBorder(BorderFactory.createEmptyBorder());
        frame.add(sp);

        text_Field = new JTextField();
        text_Field.setBounds(5, 610, 310, 40);
        text_Field.setFont(new Font("SAN_SERIF", Font.PLAIN, 16));
        frame.add(text_Field);

        text_Field.addKeyListener(new KeyAdapter() {
            public void keyPressed(KeyEvent ke) {
                l4.setText("typing...");
                t.stop();
                typing = true;
            }

            public void keyReleased(KeyEvent ke) {
                typing = false;
                if (!t.isRunning()) {
                    t.start();
                }
            }
        });

        btn = new JButton("Send");
        btn.setBounds(320, 610, 110, 40);
        btn.setBackground(new Color(7, 44, 84));
        btn.setForeground(Color.WHITE);
        btn.setFont(new Font("SAN_SERIF", Font.BOLD, 16));
        btn.addActionListener(this);
        frame.add(btn);

        //f1.getContentPane().setBackground(Color.WHITE);
        frame.setLayout(null);
        frame.setSize(450, 700);
        frame.setVisible(true);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

    }

    @Override
    public void actionPerformed(ActionEvent e) {

        try {
            String out = "";
            out = text_Field.getText();
            sendTextToFile(out);    // method call for storing data in text file "chat.txt"
            database(out);          // methid call for storing data into database "chatdb"
            JPanel p22 = formatLabel(out);

            message_area.setLayout(new BorderLayout());
            JPanel right = new JPanel(new BorderLayout());
            right.add(p22, BorderLayout.LINE_END);
            vertical.add(right);
            vertical.add(Box.createVerticalStrut(15));

            message_area.add(vertical, BorderLayout.PAGE_START);
            //a1.add(p22);
            //a1.setText(message_area.getText() + "\n\t\t\t" + out);
            dout.writeUTF(out);
            text_Field.setText("");
        } catch (Exception ex) {
            System.out.println(ex);
        }
    }

    
    // data storing method in text file
    public void sendTextToFile(String message) throws FileNotFoundException {
        try {
            FileWriter f = new FileWriter("Chat.txt", true);
            //PrintWriter p = new PrintWriter(new BufferedWriter(f));
            f.write("Irfan Khan: " + message);
            f.write(System.getProperty("line.separator"));
            f.close();
            //p.println("Irfan Khan: " + message);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // database connectivity and data stores
    public void database(String ms) {
        try {
            Class.forName("com.mysql.jdbc.Driver");
            Connection con = DriverManager.getConnection("jdbc:mysql://localhost:3306/chatdb", "root", "");
            String sql = "insert into server_msg values (?)";
            PreparedStatement pst = con.prepareStatement(sql);
            pst.setString(1, text_Field.getText());

            pst.executeUpdate();
            text_Field.setText("");
            con.close();

        } catch (Exception e) {
            JOptionPane.showMessageDialog(null, "Database Connection Error!!");
        }
    }

    public static JPanel formatLabel(String out) {
        JPanel p3 = new JPanel();
        p3.setLayout(new BoxLayout(p3, BoxLayout.Y_AXIS));

        JLabel l1 = new JLabel("<html><p style = \"width : 150px\">" + out + "</p></html>");
        l1.setBackground(new Color(37, 211, 102));
        l1.setFont(new Font("Tahoma", Font.PLAIN, 16));
        l1.setOpaque(true);
        l1.setBorder(new EmptyBorder(10, 10, 10, 50));

        Calendar cal = Calendar.getInstance();
        SimpleDateFormat sdf = new SimpleDateFormat("HH:mm");

        JLabel l2 = new JLabel();
        l2.setText(sdf.format(cal.getTime()));

        p3.add(l1);
        p3.add(l2);
        return p3;
    }

    public static void main(String[] args) {

        new Server().frame.setVisible(true);

        try {
            String msg = "";    // it will read data and then we will print it 
            skt = new ServerSocket(6005);
            s = skt.accept();
            din = new DataInputStream(s.getInputStream()); // here will be receiving data stores
            dout = new DataOutputStream(s.getOutputStream());   //sending data will be stores

            while (!msg.equals("exit")) {
                message_area.setLayout(new BorderLayout());
                msg = din.readUTF();
                JPanel p2 = formatLabel(msg);

                JPanel left = new JPanel(new BorderLayout());
                left.add(p2, BorderLayout.LINE_START);
                vertical.add(left);
                vertical.add(Box.createVerticalStrut(15));

                message_area.add(vertical, BorderLayout.PAGE_START);
                frame.validate();
                //a1.setText(message_area.getText() + "\n" + msg);
            }

            //skt.close();
            //s.close();
        } catch (Exception e) {
            //JOptionPane.showMessageDialog(null, "Something going wrong in your connectivity portion!!");
        }

    }

}
