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
 * Servlet implementation class EditCustomerServlet
 */
@WebServlet("/editCustomer")
public class EditCustomerServlet extends HttpServlet {
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
		
		// get the name of the record
		String na = req.getParameter("customer_name");
		
		try {
			
			Class.forName("org.postgresql.Driver");
			con = DriverManager.getConnection("jdbc:postgresql://localhost:5432/wave","postgres","Hacker082@");
			PreparedStatement pst = con.prepareStatement("SELECT customer_email, customer_password, "
					+ "customer_no, customer_address FROM customer where customer_name = ?");
			
			pst.setString(1, na);
			
			ResultSet rs = pst.executeQuery();
			rs.next();
			
			pw.println("<form action = 'EditCustomerURL?customer_name="+na+"' method = 'post'>");
			pw.println("<table border = '1' align = 'center'>");
			pw.println("<tr>");
			pw.println("<td>Customer Email</td>");
			pw.println("<td><input type = 'text' name = 'customerEmail' value = '" + rs.getString(1) + "'></td>");
			pw.println("</tr>");
			
			pw.println("<tr>");
			pw.println("<td>Customer Password</td>");
			pw.println("<td><input type = 'text' name = 'customerPassword' value = '" + rs.getString(2) + "'></td>");
			pw.println("</tr>");
			
			pw.println("<tr>");
			pw.println("<td>Customer Number</td>");
			pw.println("<td><input type = 'number' name = 'customerNumber' value = '" + rs.getString(3) + "'></td>");
			pw.println("</tr>");
			
			pw.println("<tr>");
			pw.println("<td>Customer Address</td>");
			pw.println("<td><input type = 'text' name = 'customerAddress' value = '" + rs.getString(4) + "'></td>");
			pw.println("</tr>");
			
			pw.println("<tr>");
			pw.println("<td><input type = 'submit' value = 'Edit'></td>");
			pw.println("<td><input type = 'reset' value = 'Cancel'></td>");
			pw.println("</tr>");
			
			pw.print("</table>");
			pw.println("</form>");
			
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
		
		
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		doGet(request, response);
	}

}
