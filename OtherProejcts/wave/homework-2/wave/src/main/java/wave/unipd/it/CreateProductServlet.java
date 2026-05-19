package wave.unipd.it;

import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;



/**
 * Servlet implementation class CreateProductServlet
 */
@WebServlet("/addproductsdata")
public class CreateProductServlet extends HttpServlet {

	private static final long serialVersionUID = 1L;
	
	
	
	@Override
	protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		String p_id = req.getParameter("id");
		String p_name = req.getParameter("name");
		int p_price = Integer.parseInt(req.getParameter("price"));
		String p_categries = req.getParameter("gender");
		int p_size = Integer.parseInt(req.getParameter("size"));
		int p_quantity = Integer.parseInt(req.getParameter("quantity"));
		String p_description = req.getParameter("description");
		
		RequestDispatcher dispatcher = null;
		
		Connection con = null;
		
		try {
			Class.forName("org.postgresql.Driver");
			con = DriverManager.getConnection("jdbc:postgresql://localhost:5432/wave","postgres","Hacker082@");
			PreparedStatement pst = con.prepareStatement("INSERT INTO products(p_id, p_name, p_price, p_categries, "
					+ "p_size, p_quantity, p_description) values(?,?,?,?,?,?,?)");
			
			pst.setString(1, p_id);
			pst.setString(2, p_name);
			pst.setInt(3, p_price);
			pst.setString(4, p_categries);
			pst.setInt(5, p_size);
			pst.setInt(6, p_quantity);
			pst.setString(7, p_description);
			
			//this method will effect the row count(will count rows)
			int rowCount = pst.executeUpdate();
			
			dispatcher = req.getRequestDispatcher("AddProduct.jsp");
			
			if(rowCount > 0) {
				req.setAttribute("status", "success");
			}else
			{
				req.setAttribute("status", "failed");
			}
			
			dispatcher.forward(req, resp);
			
		} catch (Exception e) {
			e.printStackTrace();
		}finally {
			try {
				if(con != null) {
					con.close();
					System.out.println("Disconnected from the PostgreSQL database.");
				}
				
			} catch (SQLException e2) {
				// TODO Auto-generated catch block
				e2.printStackTrace();
			}
		}
		
	}
}
