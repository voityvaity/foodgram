import styles from './styles.module.css'
import { Icons } from '..'

const Orders = ({ orders }) => {
  return <div className={styles.orders}>
    <Icons.Cart />
    {orders > 0 && (
      <span className={styles.ordersCounter}>
        {orders}
      </span>
    )}
  </div>
}

export default Orders