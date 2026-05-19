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
 * Servlet implementation class EditProductServlet
 */
@WebServlet("/editProduct")
public class EditProductServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;
       
   

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest req, HttpServletResponse res) throws ServletException, IOException {
		// TODO Auto-generated method stub
		
		//set content type
				res.setContentType("text/html");
				PrintWriter pw = res.getWriter();
				
				RequestDispatcher dispatcher = null;
				
				Connection con = null;
				
				// get the name of the record
				String id = req.getParameter("p_id");
				
				try {
					
					Class.forName("org.postgresql.Driver");
					con = DriverManager.getConnection("jdbc:postgresql://localhost:5432/wave","postgres","Hacker082@");
					PreparedStatement pst = con.prepareStatement("SELECT p_name, p_price, p_categries, "
							+ "p_size, p_quantity, p_description FROM products where p_id = ?");
					
					pst.setString(1, id);
					
					ResultSet rs = pst.executeQuery();
					rs.next();
					
					pw.println("<form action = 'EditProductURL?p_id="+id+"' method = 'post'>");
					pw.println("<table border = '1' align = 'center'>");
					pw.println("<tr>");
					pw.println("<td>Product Name</td>");
					pw.println("<td><input type = 'text' name = 'product_name' value = '" + rs.getString(1) + "'></td>");
					pw.println("</tr>");
					
					pw.println("<tr>");
					pw.println("<td>Product Price</td>");
					pw.println("<td><input type = 'text' name = 'product_price' value = '" + rs.getInt(2) + "'></td>");
					pw.println("</tr>");
					
					pw.println("<tr>");
					pw.println("<td>Product Catageries</td>");
					pw.println("<td><input type = 'text' name = 'product_categries' value = '" + rs.getString(3) + "'></td>");
					pw.println("</tr>");
					
					pw.println("<tr>");
					pw.println("<td>Product Size</td>");
					pw.println("<td><input type = 'text' name = 'product_size' value = '" + rs.getInt(4) + "'></td>");
					pw.println("</tr>");
					
					pw.println("<tr>");
					pw.println("<td>Product Quantity</td>");
					pw.println("<td><input type = 'text' name = 'product_quantity' value = '" + rs.getInt(5) + "'></td>");
					pw.println("</tr>");
					
					pw.println("<tr>");
					pw.println("<td>Product Description</td>");
					pw.println("<td><input type = 'text' name = 'product_description' value = '" + rs.getString(6) + "'></td>");
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
