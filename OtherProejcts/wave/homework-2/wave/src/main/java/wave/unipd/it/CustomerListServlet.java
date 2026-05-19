package wave.unipd.it;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Servlet implementation class CustomerListServlet
 */
@WebServlet("/CustomerList")
public class CustomerListServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest req, HttpServletResponse res) throws ServletException, IOException {
				//set content type
				res.setContentType("text/html");
				PrintWriter pw = res.getWriter();
				
				RequestDispatcher dispatcher = null;
				
				Connection con = null;
				
				try {
					
					Class.forName("org.postgresql.Driver");
					con = DriverManager.getConnection("jdbc:postgresql://localhost:5432/wave","postgres","Hacker082@");
					PreparedStatement pst = con.prepareStatement("SELECT customer_name, customer_email, customer_password, "
							+ "customer_no, customer_address FROM customer");
					
					ResultSet rs = pst.executeQuery();
					pw.println("<table border = '1' align = 'center'>");
					pw.println("<tr>");
					pw.println("<th>customer_name</th>");
					pw.println("<th>customer_email</th>");
					pw.println("<th>customer_password</th>");
					pw.println("<th>customer_no</th>");
					pw.println("<th>customer_address</th>");
					pw.println("<th>Edit</th>");
					pw.println("<th>Delete</th>");
					pw.println("</tr>");
					while(rs.next()) {					
						pw.println("<tr>");
						pw.println("<td>"+ rs.getString(1) +"</td>");
						pw.println("<td>"+ rs.getString(2) +"</td>");
						pw.println("<td>"+ rs.getInt(3) +"</td>");
						pw.println("<td>"+ rs.getInt(4) +"</td>");
						pw.println("<td>"+ rs.getString(5) +"</td>");
						pw.println("<td><a href = 'editCustomer?customer_name=" + rs.getString(1) +"'>Edit</a></td>");
						pw.println("<td><a href = 'deleteCustomer?customer_name=" + rs.getString(1) +"'>Delete</a></td>");
						
						pw.println("</tr>");
					}
					pw.println("</table>");
				} catch (Exception e) {
					e.printStackTrace();
				}finally {
					try {
						
						if(con != null) {
							con.close();
							System.out.println("Disconnected from the PostgreSQL database.");
						}
						
					} catch (Exception e2) {
						// TODO: handle exception
						e2.printStackTrace();
					}
				}
				
				pw.println("<a href = 'index.jsp'> Home Page</a>");
				pw.println("<br>");
				pw.println("<a href = 'AddCustomers.jsp'> Add Members</a>");
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest req, HttpServletResponse res) throws ServletException, IOException {
		
		
		doGet(req, res);
	}

}
